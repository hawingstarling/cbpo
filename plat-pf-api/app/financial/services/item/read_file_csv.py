import os


class ReadFileCsv:
    def __init__(self, source_file_path: str, chunks: int = 5000):
        assert os.path.isfile(source_file_path), "file does not exist"
        assert source_file_path[-4:] == '.csv', "csv only"

        self.__source_file_path = source_file_path
        self.__chunk_rows = chunks
        self.__headers: [str] = ['sku', 'brand', 'asin']

    def __split_into_parts(self):
        with open(self.__source_file_path, 'r') as file:
            yield_start_at = 1
            yield_end_at = 1

            for index_file, line in enumerate(file):
                if index_file == 0:
                    # ignore headers
                    continue

                if index_file % self.__chunk_rows == 0:
                    yield_end_at = index_file
                    yield self.__read_part(yield_start_at, yield_end_at)
                    yield_start_at = yield_end_at + 1

                yield_end_at += 1
            yield self.__read_part(yield_start_at, yield_end_at - 1)

    def __read_part(self, start_index, end_index):
        """
        return generator of data
        :param start_index:
        :param end_index:
        """
        with open(self.__source_file_path, 'r') as file:
            for index_file, line in enumerate(file):
                if start_index <= index_file <= end_index:
                    row_values = line.replace('\n', '').split(',')
                    yield {item_header: row_values[_index_header] for _index_header, item_header in
                           enumerate(self.__headers)}

    def read_parts(self):
        """
        return generator of parts
        :return:
        """
        return self.__split_into_parts()
