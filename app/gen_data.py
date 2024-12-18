import random
import faker
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from faker.config import AVAILABLE_LOCALES


'''
Может долго производиться очистка базы
В связи с ограничением уникальных слов
в русском словаре faker, пришлось
использовать все локали
'''
def generate_data():
    User.objects.all().delete()
    Profile.objects.all().delete()
    Question.objects.all().delete()
    Answer.objects.all().delete()
    Tag.objects.all().delete()
    QuestionLike.objects.all().delete()
    AnswerLike.objects.all().delete()

    num_users = 15000
    num_tags = 10000
    num_questions = 100000
    num_answers = 1000000
    num_likes = 2000000

    print("Generating users...")
    fake = faker.Faker('ru_RU')
    users = []
    for _ in range(num_users):
        username = fake.unique.user_name()
        email = fake.unique.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        users.append(
            User(
                username=username,
                email=email,
                password="password",
                first_name=first_name,
                last_name=last_name,
            )
        )
    User.objects.bulk_create(users, batch_size=1000)

    print("Generating profiles...")
    profiles = []
    for user in User.objects.all():
        avatar_url = f"https://picsum.photos/seed/{user.username}/200/200"
        profiles.append(Profile(user=user, avatar=avatar_url))
    Profile.objects.bulk_create(profiles, batch_size=1000)

    print("Generating tags...")
    fake = faker.Faker(AVAILABLE_LOCALES)
    tags = []
    try:
        for _ in range(num_tags):
            tags.append(Tag(name=fake.unique.word()))
    except:
        pass
    Tag.objects.bulk_create(tags, batch_size=1000)
    fake = faker.Faker('ru_RU')

    print("Generating questions...")
    tags = list(Tag.objects.all())
    users = list(User.objects.all())
    questions = []
    for _ in range(num_questions):
        title = fake.sentence(nb_words=6)
        text = fake.paragraph(nb_sentences=random.randint(3, 10))
        questions.append(
            Question(
                title=title,
                text=text,
                author=random.choice(users),
            )
        )
    Question.objects.bulk_create(questions, batch_size=1000)

    print("Adding tags to questions...")
    questions = Question.objects.all()
    through_model = Question.tags.through
    question_tags = []
    for question in questions:
        for tag in random.sample(tags, random.randint(1, 5)):
            question_tags.append(
                through_model(question_id=question.id, tag_id=tag.id)
            )
    through_model.objects.bulk_create(question_tags, batch_size=1000)

    print("Generating answers...")
    questions = list(questions)
    answers = []
    for _ in range(num_answers):
        text = fake.paragraph(nb_sentences=random.randint(2, 6))
        answers.append(
            Answer(
                text=text,
                author=random.choice(users),
                question=random.choice(questions),
                is_correct=random.choice([True, False]),
            )
        )
    Answer.objects.bulk_create(answers, batch_size=1000)

    print("Generating question likes...")
    likes = set()

    while len(likes) < num_likes:
        user = random.choice(users)
        question = random.choice(questions)
        like_key = (user.id, question.id)

        if like_key not in likes:
            likes.add(like_key)

    question_likes = [QuestionLike(user_id=user_id, question_id=question_id) for user_id, question_id in likes]
    QuestionLike.objects.bulk_create(question_likes, batch_size=1000)

    print("Generating answer likes...")
    answers = list(Answer.objects.all())
    answer_likes = []
    for _ in range(num_likes):
        answer_likes.append(
            AnswerLike(
                user=random.choice(users),
                answer=random.choice(answers),
            )
        )

    AnswerLike.objects.bulk_create(answer_likes, batch_size=1000)
