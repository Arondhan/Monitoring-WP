"""
Скрипт инициализации базы данных тестовыми доменами
Запускается после старта приложения для демонстрации
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Добавляем корень backend в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.domain import Domain


async def seed_data():
    """Добавление тестовых доменов"""

    # Популярные сайты для демонстрации
    test_domains = [
        {
            "name": "Google",
            "url": "https://www.google.com",
            "check_interval_seconds": 300,
        },
        {
            "name": "GitHub",
            "url": "https://github.com",
            "check_interval_seconds": 300,
        },
        {
            "name": "Stack Overflow",
            "url": "https://stackoverflow.com",
            "check_interval_seconds": 300,
        },
    ]

    async with async_session_maker() as session:
        for domain_data in test_domains:
            # Проверяем существует ли домен
            existing = await session.execute(
                select(Domain).where(Domain.url == domain_data["url"])
            )

            if not existing.scalar_one_or_none():
                domain = Domain(
                    name=domain_data["name"],
                    url=domain_data["url"],
                    check_interval_seconds=domain_data["check_interval_seconds"],
                    last_status="PENDING",
                )
                session.add(domain)
                print(f"Added domain: {domain_data['name']} ({domain_data['url']})")
            else:
                print(f"Domain already exists: {domain_data['name']}")

        await session.commit()

    print("\nSeed data completed!")


if __name__ == "__main__":
    asyncio.run(seed_data())
