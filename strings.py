import zlib


# Функция для сжатия строки
def compress_string(s):
    return zlib.compress(s.encode())


# функция для распаковки сжжатой строки
def decompress_string(compressed):
    # распаковываем сжатые 'compress' из буфера
    decompress = zlib.decompress(compressed)
    # преобразуем байты в текст
    text = decompress.decode('utf-8')
    return text
