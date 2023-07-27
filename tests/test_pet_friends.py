import pytest

from api import PetFriends
from settings import valid_email, valid_password, invalid_password, invalid_email
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер', age='5', pet_photo='images\\cat1.jpg'):
    """Добавление с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images\\cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")


def test_successful_create_pet_simple(name='Pushok', animal_type='cat', age='3'):
    """Проверяем, что возможно добавить питомца с валидными данными без фото"""
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert 'id' in result
    assert result['name'] == name
    assert result['age'] == age
    assert result['animal_type'] == animal_type


def test_set_photo_on_pets_by_id(pet_photo='images\\cat1.jpg'):
    """Проверяем, что возможно добавить фото питомцу из списка моих питомцев по его id"""

    # определяем путь к фото
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем: если список своих питомцев пустой, то добавляем нового питомца без фото и снова запрашиваем список
    # своих питомцев
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Барсик", "кот", "1")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.set_photo_by_pet_id(auth_key, pet_id, pet_photo)
    assert status == 200
    assert 'error' not in result


def test_no_auth_key_for_invalid_password(email=valid_email, password=invalid_password):
    """ Проверяем, что запрос на получение api ключа возвращает статус 403, и в результате запроса не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа - в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с ожидаемым результатом
    assert status == 403
    assert 'key' not in result


def test_no_auth_key_for_invalid_email(email=invalid_email, password=valid_password):
    """ Проверяем, что запрос на получение api ключа возвращает статус 403, и в результате запроса не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа - в result
    status, _ = pf.get_api_key(email, password)

    # Сверяем полученные данные с ожидаемым результатом
    assert status == 403


def test_no_pets_shown_for_unauthorized_user(filter=''):
    """ Проверяем, что запрос на получение списка всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее, используя этот ключ,
    запрашиваем список всех питомцев и проверяем, что список полученных питомцев не пустой.
    Доступные значения параметра filter: 'my_pets' либо '' """

    auth_key = {'key': ''}
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403
    assert 'pets' not in result


def test_required_fields_for_adding_new_pet(name='', animal_type='', age='', pet_photo='images/cat1.jpg'):
    """Проверяем, что возможно добавить питомца без заполнения обязательных полей"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, _ = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200


def test_unsuccessful_delete_pet_for_unauthorized_user_403():
    """Проверяем, что неавторизованный пользователь не может удалить питомца"""

    # Получаем ключ auth_key и создаем питомца, запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pf.add_new_pet(auth_key, "Васька", "кот", "4", "images/cat1.jpg")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id последнего питомца из списка и отправляем запрос на удаление неавторизованным пользователем
    pet_id = my_pets['pets'][-1]['id']
    auth_key = {"key": ""}
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем что статус ответа равен 403
    assert status == 403


def test_error_400_for_updating_not_existing_pet(pet_id="01234567891234", name='', animal_type='', age=-1):
    """Проверяем, что данные несуществующего питомца нельзя обновить"""

    # Получаем ключ auth_key и пробуем обновить имя, тип и возраст несуществующего питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, _ = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем что статус ответа = 400
    assert status == 400


def test_error_500_for_set_photo_on_not_existing_pet(pet_photo='images/cat1.jpg'):
    """Проверяем, добавление фото с неправильным айди возникает 500 ошибка"""

    # определяем путь к фото
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Берём несуществующий id питомца из и отправляем запрос на добавление фото
    pet_id = "01234567891234"
    status, _ = pf.set_photo_by_pet_id(auth_key, pet_id, pet_photo)
    assert status == 500


def test_add_new_pet_with_valid_data_no_photo_no_name_negative_age(name='', animal_type='неизвестно', age='987654'):
    """Проверяем, что возможно добавить с пустыми данныеми"""
    # Запрашиваем ключ api и сохраняем в переменную auth_key.
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца.
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    # Сверяем полученный ответ с ожидаемым результатом.
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age