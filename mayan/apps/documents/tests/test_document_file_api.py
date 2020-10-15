from django.utils.encoding import force_text

from rest_framework import status

from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import Document, DocumentType
from ..permissions import (
    permission_document_create, permission_document_file_download,
    permission_trashed_document_delete, permission_document_edit,
    permission_document_file_delete, permission_document_file_view,
    permission_document_file_new, permission_document_properties_edit,
    permission_trashed_document_restore, permission_document_trash,
    permission_document_view, permission_document_type_create,
    permission_document_type_delete, permission_document_type_edit,
    permission_document_version_view,
)

from .literals import (
    TEST_DOCUMENT_DESCRIPTION_EDITED, TEST_PDF_DOCUMENT_FILENAME,
    TEST_DOCUMENT_TYPE_LABEL, TEST_DOCUMENT_TYPE_2_LABEL,
    TEST_DOCUMENT_TYPE_LABEL_EDITED, TEST_DOCUMENT_VERSION_COMMENT_EDITED,
    TEST_SMALL_DOCUMENT_FILENAME
)
from .mixins.document_mixins import (
    DocumentAPIViewTestMixin, DocumentTestMixin
)
from .mixins.document_file_mixins import (
    DocumentFileAPIViewTestMixin, DocumentFileTestMixin,
    DocumentFilePageAPIViewTestMixin
)
from .mixins.document_type_mixins import DocumentTypeAPIViewTestMixin
from .mixins.document_version_mixins import (
    DocumentVersionAPIViewTestMixin, DocumentVersionTestMixin,
    DocumentVersionPageAPIViewTestMixin
)
from .mixins.trashed_document_mixins import TrashedDocumentAPIViewTestMixin


class DocumentFileAPIViewTestCase(
    DocumentFileAPIViewTestMixin, DocumentTestMixin,
    DocumentFileTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def test_document_file_api_download_view_no_permission(self):
        self._upload_test_document()

        response = self._request_test_document_file_api_download_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_file_api_download_view_with_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_document_file_download
        )

        response = self._request_test_document_file_api_download_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.test_document.latest_file.open() as file_object:
            self.assert_download_response(
                response=response, content=file_object.read(),
                filename=force_text(self.test_document.latest_file),
                mime_type=self.test_document.latest_file.mimetype
            )

    def test_document_file_api_download_preserve_extension_view(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_document_file_download
        )

        response = self.get(
            viewname='rest_api:documentfile-download', kwargs={
                'document_id': self.test_document.pk,
                'document_file_id': self.test_document.latest_file.pk,
            }, data={'preserve_extension': True}
        )

        with self.test_document.latest_file.open() as file_object:
            self.assert_download_response(
                response=response, content=file_object.read(),
                filename=self.test_document.latest_file.get_rendered_string(
                    preserve_extension=True
                ), mime_type=self.test_document.latest_file.mimetype
            )

    def test_document_file_api_list_view_no_permission(self):
        self._upload_test_document()
        self._upload_new_file()

        response = self._request_test_document_file_api_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['count'], 0)

    def test_document_file_api_list_view_with_access(self):
        self._upload_test_document()
        self._upload_new_file()

        self.grant_access(
            obj=self.test_document, permission=permission_document_file_view
        )
        response = self._request_test_document_file_api_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['results'][1]['checksum'],
            self.test_document.latest_file.checksum
        )
    def test_document_file_api_delete_view_no_permission(self):
        self._upload_test_document()
        self._upload_new_file()

        response = self._request_test_document_file_api_delete_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_file_api_delete_view_with_access(self):
        self._upload_test_document()
        self._upload_new_file()
        self.grant_access(
            obj=self.test_document,
            permission=permission_document_file_delete
        )

        response = self._request_test_document_file_api_delete_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(self.test_document.files.count(), 1)
        self.assertEqual(
            self.test_document.files.first(), self.test_document.latest_file
        )

    def test_document_file_api_upload_view_no_permission(self):
        self._upload_test_document()

        response = self._request_test_document_file_api_upload_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_document_file_api_upload_view_with_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_document_file_new
        )

        response = self._request_test_document_file_api_upload_view()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertEqual(self.test_document.files.count(), 2)
        self.assertEqual(self.test_document.latest_file.exists(), True)
        self.assertEqual(self.test_document.latest_file.size, 272213)
        self.assertEqual(self.test_document.latest_file.mimetype, 'application/pdf')
        self.assertEqual(self.test_document.latest_file.encoding, 'binary')
        self.assertEqual(
            self.test_document.latest_file.checksum,
            'c637ffab6b8bb026ed3784afdb07663fddc60099853fae2be93890852a69ecf3'
        )
        self.assertEqual(self.test_document.page_count, 47)


class DocumentFilePageAPIViewTestCase(
    DocumentFilePageAPIViewTestMixin, DocumentTestMixin, BaseAPITestCase
):
    def test_document_file_page_api_image_view_no_permission(self):
        response = self._request_document_file_page_image()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_file_page_api_image_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_file_view
        )

        response = self._request_document_file_page_image()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentTypeAPIViewTestCase(
    DocumentTypeAPIViewTestMixin, DocumentTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False
    auto_create_test_document_type = False

    def test_document_type_api_create_view_no_permission(self):
        response = self._request_test_document_type_api_create_view()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(DocumentType.objects.all().count(), 0)

    def test_document_type_api_create_view_with_permission(self):
        self.grant_permission(permission=permission_document_type_create)

        response = self._request_test_document_type_api_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(DocumentType.objects.all().count(), 1)
        self.assertEqual(
            DocumentType.objects.all().first().label,
            TEST_DOCUMENT_TYPE_LABEL
        )

    def test_document_type_api_delete_view_no_permission(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        response = self._request_test_document_type_api_delete_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_type_api_delete_view_with_access(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )
        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_delete
        )

        response = self._request_test_document_type_api_delete_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(DocumentType.objects.all().count(), 0)

    def test_document_type_api_edit_via_patch_view_no_permission(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        response = self._request_test_document_type_api_patch_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_type_api_edit_via_patch_view_with_access(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )
        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_edit
        )

        response = self._request_test_document_type_api_put_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_document_type.refresh_from_db()
        self.assertEqual(
            self.test_document_type.label, TEST_DOCUMENT_TYPE_LABEL_EDITED
        )

    def test_document_type_api_edit_via_put_view_no_permission(self):
        self._create_test_document_type()

        response = self._request_test_document_type_api_put_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_type_api_edit_via_put_view_with_access(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )
        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_edit
        )

        response = self._request_test_document_type_api_put_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_document_type.refresh_from_db()
        self.assertEqual(
            self.test_document_type.label, TEST_DOCUMENT_TYPE_LABEL_EDITED
        )
