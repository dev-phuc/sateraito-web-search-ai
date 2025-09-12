class FirestoreDB:
    @classmethod
    def set_doc(cls, doc_ref, doc):
        doc_ref.set(doc)

    @classmethod
    def add_doc(cls, collection_ref, doc):
        _, doc_ref = collection_ref.add(doc)
        return doc_ref.id
    
    @classmethod
    def update_doc(cls, doc_ref, new_data):
        doc_ref.update(new_data)

    @classmethod
    def delete_doc(cls, doc_ref):
        doc_ref.delete()

    @classmethod
    def get_doc(cls, doc_ref):
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None