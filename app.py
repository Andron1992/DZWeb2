import pickle
from datetime import datetime
from abc import ABC, abstractmethod


class Field:
    pass


class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be a 10-digit number.")
        self.value = value


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, value):
        for phone in self.phones:
            if phone.value == value:
                raise ValueError("Phone number already exists.")
        self.phones.append(Phone(value))

    def add_birthday(self, value):
        self.birthday = Birthday(value)


class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_record(self, record):
        self.contacts.append(record)

    def find(self, name):
        for contact in self.contacts:
            if contact.name.value.lower() == name.lower():
                return contact
        return None


# Abstract base class for user views
class UserView(ABC):
    @abstractmethod
    def display_message(self, message):
        pass

    @abstractmethod
    def display_contacts(self, contacts):
        pass


# Console view implementation
class ConsoleView(UserView):
    def display_message(self, message):
        print(message)

    def display_contacts(self, contacts):
        if contacts:
            contact_info = []
            for contact in contacts:
                phones = ', '.join([phone.value for phone in contact.phones]) if contact.phones else "No phone"
                birthday = contact.birthday.value.strftime('%d.%m.%Y') if contact.birthday else "No birthday"
                contact_info.append(f"{contact.name.value}: {phones}, Birthday: {birthday}")
            print("\n".join(contact_info))
        else:
            print("Address book is empty.")


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Invalid command. Use 'add [name] [phone]'."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
        message += f" Phone number: {phone}"
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Invalid command. Please use 'change [name] [new_phone]'."
    name, new_phone = args
    record = book.find(name)
    if record:
        record.phones = []
        record.add_phone(new_phone)
        return f"Phone number changed for {name}."
    else:
        return f"Contact {name} not found."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        return "Invalid command. Use 'phone [name]'."
    name = args[0]
    record = book.find(name)
    if record and record.phones:
        return f"{name}'s phone number is: {', '.join([phone.value for phone in record.phones])}"
    elif record:
        return f"{name} doesn't have a phone number set."
    else:
        return f"Contact {name} not found."


@input_error
def show_all_contacts(book: AddressBook):
    return book.contacts


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Invalid command. Use 'add-birthday [name] [date]'."
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return f"Birthday added for {name}."
    else:
        return f"Contact {name} not found."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Invalid command. Use 'show-birthday [name]'."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is: {record.birthday.value.strftime('%d.%m.%Y')}"
    elif record:
        return f"{name} doesn't have a birthday set."
    else:
        return f"Contact {name} not found."


@input_error
def birthdays(book: AddressBook):
    all_birthdays = []
    for contact in book.contacts:
        if contact.birthday:
            all_birthdays.append(f"{contact.name.value}: {contact.birthday.value.strftime('%d.%m.%Y')}")
    if all_birthdays:
        return "\n".join(all_birthdays)
    else:
        return "No birthdays found."


def hello():
    return "Hello! How can I help you?"


def close():
    return "Goodbye!"


def exit():
    return "Goodbye!"


def help_command():
    commands = [
        "hello - Greetings from the bot",
        "add [name] [phone] - Add a contact with a phone number",
        "change [name] [new_phone] - Change the phone number of an existing contact",
        "phone [name] - Show the phone number of a contact",
        "all - Show all contacts",
        "add-birthday [name] [date] - Add a birthday to a contact",
        "show-birthday [name] - Show the birthday of a contact",
        "birthdays - Show all birthdays",
        "close, exit - Exit the program",
        "help - Show this help message"
    ]
    return "\n".join(commands)


def parse_input(user_input):
    return user_input.split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return AddressBook()  # Return a new address book if the file is not found or corrupted


def view_factory(view_type="console"):
    if view_type == "console":
        return ConsoleView()
    # Future views can be added here
    raise ValueError("Unknown view type.")


def main():
    book = load_data()
    view = view_factory("console")
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            view.display_message("You didn't enter any command.")
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            view.display_message("Goodbye!")
            break

        elif command == "hello":
            view.display_message("How can I help you?")

        elif command == "add":
            view.display_message(add_contact(args, book))

        elif command == "change":
            view.display_message(change_contact(args, book))

        elif command == "phone":
            view.display_message(show_phone(args, book))

        elif command == "all":
            contacts = show_all_contacts(book)
            view.display_contacts(contacts)

        elif command == "add-birthday":
            view.display_message(add_birthday(args, book))

        elif command == "show-birthday":
            view.display_message(show_birthday(args, book))

        elif command == "birthdays":
            view.display_message(birthdays(book))

        elif command == "help":
            view.display_message(help_command())

        else:
            view.display_message("Invalid command. Type 'help' to see the list of available commands.")


if __name__ == "__main__":
    main()
