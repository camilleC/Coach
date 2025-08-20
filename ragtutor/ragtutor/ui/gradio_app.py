import asyncio
import logging
import os
from typing import Tuple

import gradio as gr

from ..core.rag_service import RAGService
from ..config.settings import settings


logger = logging.getLogger(__name__)


class RAGGradioInterface:
    def __init__(self):
        self.rag_service = None

    async def initialize(self):
        self.rag_service = RAGService()
        await self.rag_service.initialize()

    def query_wrapper(self, query: str, collection: str, top_k: int) -> Tuple[str, str]:
        """Wrapper for async query function"""
        try:
            if not self.rag_service:
                return "❌ RAG service not initialized", ""

            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.rag_service.query(
                    query=query,
                    top_k=top_k,
                    collection_name=collection if collection else None,
                )
            )

            sources_text = ""
            if result.get("sources"):
                sources_text = "\n\n**Sources:**\n"
                for i, source in enumerate(result["sources"][:3], 1):
                    sources_text += f"{i}. Page {source['metadata'].get('page', '?')}: {source['text'][:100]}...\n"

            return result["answer"] + sources_text, ""

        except Exception as e:
            logger.error(f"Gradio query failed: {e}")
            return f"❌ Error: {str(e)}", ""

    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="RAG Tutor - Document Q&A", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 📚 RAG Tutor - Document Q&A System")
            gr.Markdown("Ask questions about your uploaded documents and get AI-powered answers with source citations.")

            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="e.g., What are the key principles of effective coaching?",
                        lines=3,
                    )

                    with gr.Row():
                        collection_input = gr.Textbox(
                            label="Collection Name (optional)",
                            placeholder="Leave empty for default collection",
                        )
                        top_k_slider = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Number of Sources",
                        )

                    submit_btn = gr.Button("🔍 Ask Question", variant="primary")

                with gr.Column(scale=3):
                    output = gr.Markdown(label="Answer")

            submit_btn.click(
                fn=self.query_wrapper,
                inputs=[query_input, collection_input, top_k_slider],
                outputs=[output, query_input],
            )

            query_input.submit(
                fn=self.query_wrapper,
                inputs=[query_input, collection_input, top_k_slider],
                outputs=[output, query_input],
            )

            gr.Markdown(
                """
            ### Example Questions:
            - "What are the main coaching techniques mentioned in the document?"
            - "How should I prepare for a coaching session?"
            - "What are the ethical guidelines for coaches?"
            """
            )

        return demo


def create_app():
    interface = RAGGradioInterface()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(interface.initialize())
    return interface.create_interface()


def main():
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=False)


if __name__ == "__main__":
    main()


