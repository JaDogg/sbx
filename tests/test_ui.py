from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock, patch

from sbx.ui.controls import MarkdownArea


class UiTestCase(TestCase):
    def test_document_tab(self):
        mock_document = MagicMock()
        with patch(
            "sbx.ui.controls.MarkdownArea.document", new_callable=PropertyMock
        ) as mock_doc:
            mock_doc.return_value = mock_document
            markdown = MarkdownArea()
            markdown.indent()
            self.assertTrue(
                "call.paste_clipboard_data" in str(mock_document.mock_calls)
            )

    def test_document_tab_readonly(self):
        mock_document = MagicMock()
        with patch(
            "sbx.ui.controls.MarkdownArea.document", new_callable=PropertyMock
        ) as mock_doc:
            mock_doc.return_value = mock_document
            markdown = MarkdownArea(readonly=True)
            markdown.indent()
            self.assertTrue(
                "call.paste_clipboard_data"
                not in str(mock_document.mock_calls)
            )
