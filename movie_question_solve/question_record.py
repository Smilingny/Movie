from movie_main.models import User


def add_record(name, question, answer):
    person = User.objects.get(account=name)
    QA = question + '\t' + answer + '\n'
    print(QA)
    person.record = person.record + QA
    person.save()


def get_all_record(name):
    person = User.objects.get(account=name)
    return person.record


def delete_all_record(name):
    person = User.objects.get(account=name)
    person.record = ""
    person.save()
