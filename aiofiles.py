import asyncio
import aiofiles
import aiofiles.os
import os

class AsyncLogManager:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.categories = ['INFO', 'ERROR', 'DEBUG']

    async def setup(self):
        """Использование aiofiles.os для подготовки окружения."""
        # 1. aiofiles.os.path.exists: Асинхронная проверка пути
        if await aiofiles.os.path.exists(self.output_dir):
            # 2. aiofiles.os.remove: Удаление старых файлов внутри директории (пример)
            for file in os.listdir(self.output_dir):
                await aiofiles.os.remove(os.path.join(self.output_dir, file))
        else:
            # 3. aiofiles.os.mkdir: Асинхронное создание папки
            await aiofiles.os.mkdir(self.output_dir)

    async def generate_mock_data(self, lines=1000):
        """Генерация тестового файла через асинхронную запись."""
        print(f"Генерация {self.input_file}...")
        # 4. aiofiles.open: Асинхронное открытие для записи
        async with aiofiles.open(self.input_file, mode='w', encoding='utf-8') as f:
            for i in range(lines):
                cat = self.categories[i % 3]
                # 5. f.write: Асинхронная запись строки
                await f.write(f"{cat}: Log message ID {i} timestamp {os.urandom(4).hex()}\n")

    async def process_logs(self):
        """Чтение и распределение логов по файлам."""
        # Словарь открытых дескрипторов файлов для записи
        writers = {
            cat: await aiofiles.open(os.path.join(self.output_dir, f"{cat.lower()}.log"), mode='a')
            for cat in self.categories
        }

        print("Начало обработки...")
        # 6. Асинхронная итерация по строкам файла
        async with aiofiles.open(self.input_file, mode='r') as f:
            async for line in f:
                for cat in self.categories:
                    if line.startswith(cat):
                        await writers[cat].write(line)
                        # 7. f.flush: Принудительный сброс буфера (если критично)
                        await writers[cat].flush()

        # Закрываем все файлы
        for w in writers.values():
            await w.close()

    async def finalize(self):
        """Демонстрация работы с метаданными через aiofiles.os."""
        # 8. aiofiles.os.stat: Получение размера файла асинхронно
        stats = await aiofiles.os.stat(self.input_file)
        print(f"Обработка завершена. Исходный файл: {stats.st_size} байт")
        
        # 9. aiofiles.os.rename: Переименование (архивация) исходника
        archive_name = f"processed_{self.input_file}"
        await aiofiles.os.rename(self.input_file, archive_name)
        print(f"Исходный файл переименован в {archive_name}")

async def main():
    manager = AsyncLogManager("server.log", "logs_dist")
    
    await manager.setup()
    await manager.generate_mock_data(5000)
    await manager.process_logs()
    await manager.finalize()

if __name__ == "__main__":
    asyncio.run(main())
