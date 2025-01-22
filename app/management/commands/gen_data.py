import random
from datetime import timedelta

import faker
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными. Использование: python manage.py fill_db [ratio]"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Коэффициент заполнения базы данных")

    def handle(self, *args, **kwargs):
        ratio = kwargs["ratio"]

        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_likes = ratio * 200 * 2

        self.stdout.write(self.style.WARNING(f"Заполняем базу с ratio = {ratio}"))
        self.stdout.write("Очистка базы данных...")
        User.objects.all().delete()
        Profile.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        Tag.objects.all().delete()
        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()

        self.stdout.write("Генерация пользователей...")
        fake = faker.Faker("ru_RU")
        users = [
            User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password="password",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            for _ in range(num_users)
        ]
        User.objects.bulk_create(users, batch_size=1000)
        users = list(User.objects.all())

        self.stdout.write("Генерация профилей...")
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        profiles = []
        for user in users:
            avatar_url = f"https://picsum.photos/seed/{user.username}/200/200"
            avatar_name = f"avatars/{user.username}_avatar.jpg"

            response = requests.get(avatar_url)
            if response.status_code == 200:
                avatar_file = ContentFile(response.content)

                # Save the file and get the relative path
                avatar_path = fs.save(avatar_name, avatar_file)

                # Only store relative path in the Profile model
                profile = Profile(user=user, avatar=avatar_path)

                profiles.append(profile)

            else:
                self.stdout.write(self.style.ERROR(f"Ошибка скачивания изображения для {user.username}"))

        Profile.objects.bulk_create(profiles, batch_size=1000)

        self.stdout.write("Генерация тегов...")
        tag_names = set()

        while len(tag_names) < num_tags:
            word = fake.word()
            if word in tag_names:
                word = f"{word}_{random.randint(100, 999)}"
            tag_names.add(word)

        tags = [Tag(name=name) for name in tag_names]
        Tag.objects.bulk_create(tags, batch_size=1000)
        tags = list(Tag.objects.all())

        self.stdout.write("Генерация вопросов...")
        questions = [
            Question(
                title=fake.sentence(nb_words=6),
                text=fake.paragraph(nb_sentences=random.randint(3, 10)),
                author=random.choice(users),
                created_at=now() - timedelta(days=random.randint(1, 365)),
            )
            for _ in range(num_questions)
        ]
        Question.objects.bulk_create(questions, batch_size=1000)
        questions = list(Question.objects.all())

        self.stdout.write("Добавление тегов к вопросам...")
        through_model = Question.tags.through
        question_tags = set()

        for question in questions:
            available_tags = list(tags)
            num_assigned_tags = random.randint(1, 5)

            for tag in random.sample(available_tags, num_assigned_tags):
                question_tags.add((question.id, tag.id))

        through_model.objects.bulk_create(
            [through_model(question_id=q, tag_id=t) for q, t in question_tags], batch_size=1000
        )

        self.stdout.write("Генерация ответов...")
        answers = [
            Answer(
                text=fake.paragraph(nb_sentences=random.randint(2, 6)),
                author=random.choice(users),
                question=random.choice(questions),
                is_correct=random.choice([True, False]),
                created_at=now() - timedelta(days=random.randint(1, 365)),
            )
            for _ in range(num_answers)
        ]
        Answer.objects.bulk_create(answers, batch_size=1000)
        answers = list(Answer.objects.all())

        self.stdout.write("Генерация лайков к вопросам...")
        question_likes = set()
        available_pairs = [(user.id, question.id) for user in users for question in questions]
        selected_likes = random.sample(available_pairs, min(num_likes // 2, len(available_pairs)))

        for user_id, question_id in selected_likes:
            is_like = random.choice([True, False])
            question_likes.add((user_id, question_id, is_like))

        QuestionLike.objects.bulk_create(
            [QuestionLike(user_id=u, question_id=q, is_like=is_like) for u, q, is_like in question_likes],
            batch_size=1000
        )

        self.stdout.write("Генерация лайков к ответам...")
        answer_likes = set()
        available_pairs = [(user.id, answer.id) for user in users for answer in answers]
        selected_likes = random.sample(available_pairs, min(num_likes // 2, len(available_pairs)))

        for user_id, answer_id in selected_likes:
            is_like = random.choice([True, False])
            answer_likes.add((user_id, answer_id, is_like))

        AnswerLike.objects.bulk_create(
            [AnswerLike(user_id=u, answer_id=a, is_like=is_like) for u, a, is_like in answer_likes], batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS("✅ Генерация данных завершена!"))
