class SourceDocumentAbstract:
    def _create_docs_actions(self, *args, **kwargs):
        raise NotImplementedError

    def create_index(self, *args, **kwargs):
        raise NotImplementedError

    def on_validate(self, *args, **kwargs):
        raise NotImplementedError

    def on_process(self, *args, **kwargs):
        raise NotImplementedError

    def on_complete(self, *args, **kwargs):
        raise NotImplementedError
