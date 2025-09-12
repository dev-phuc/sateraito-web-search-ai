class RealTimeDB:
    @classmethod
    def read_data(self, ref):
        return ref.get()

    @classmethod
    def write_data(self, ref, data):
        ref.set(data)
    
    @classmethod
    def update_data(self, ref, data):
        ref.update(data)
    
    @classmethod
    def delete_data(self, ref):
        ref.delete()
    
    @classmethod
    def push_data(self, ref, data):
        new_data_ref = ref.push()
        new_data_ref.set(data)
        return new_data_ref.key
    
    @classmethod
    def get_key(self, ref):
        return ref.key