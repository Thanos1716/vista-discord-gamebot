import discord

from file_manager import exec_sql, save_db_filepath


class Object:
    def __init__(self, object_id):
        self.object_class, self.class_id, self.location, self.column_name = \
            exec_sql(save_db_filepath, f"SELECT object_class, class_id, location, column_name FROM objects "
                                       f"WHERE object_id = {object_id}")


class Item(Object):
    def __init__(self, object_id):
        super().__init__(object_id)
        self.name, self.description, self.weight, self.size, self.emoji, self.image = \
            exec_sql(save_db_filepath, f"SELECT name, description, weight, size, emoji, image_link "
                                       f"FROM {self.object_class} WHERE {self.column_name} = {self.class_id}")

    def embed_item(self):
        out = discord.Embed(title=self.name, description=self.description, colour=0x88FF42)
        if isinstance(self.image, str):
            out.set_thumbnail(url=self.image)
        return out

    def move_item(self, target):
        # if target in execute_sql(filepath, "SELECT COUNT(1) FROM objects WHERE location={} AND object_id={};".format(self.location, self.object_id)):
        # print(execute_sql(filepath, "select location from objects where object_id = {}".format(self.object_id)))
        exec_sql(save_db_filepath, f"UPDATE objects SET location = '{target}' WHERE object_id = {self.object_id}")
        # print(execute_sql(filepath, "select location from objects where object_id = {}".format(self.object_id)))
        self.location = target
        # else:
        #     raise Exception("{} not in {}".format(target, filepath))


class Container:
    def __init__(self, size=10):
        self.size = size
        self.contents = []

    def add_object(self, object_id):
        self.contents.append(object_id)

    def embed_contents(self):
        description = ""
        for i in self.contents:
            description += str(i.name) + " " + str(i.emoji) + "\n"
        print(description)
        return description


class Player(Object, Container):
    def __init__(self, object_id):
        Object.__init__(self, object_id)
        Container.__init__(self, 36)
        self.name, self.hunger, self.thirst, self.health, self.stamina, self.strength = exec_sql(
            save_db_filepath, f"SELECT name, hunger, thirst, health, stamina, strength FROM players "
                              f"WHERE player_id = {self.class_id}")


if __name__ == "__main__":
    # Thanos = Player(2)
    iksvo = Player(4)
    iksvo.add_object(Item(1))
    iksvo.add_object(Item(3))
    iksvo.add_object(Player(2))

    print(iksvo.column_name)
    # print(iksvo.embed_contents())
    print(iksvo.contents[1].embed_item())
    print(iksvo.contents[2].health)


# class Vehicle(Object):
#     pass
#
#
# class Abstract:
#     pass
#
#
# class NonPlayerCharacter:
#     pass
#
#
# class Location:
#     pass
