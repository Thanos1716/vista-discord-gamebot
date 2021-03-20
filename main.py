from commands import *
from file_manager import exec_sql, save_db_filepath
from object import *
import os


def init():
    object_ids = exec_sql(save_db_filepath, "SELECT object_id, object_class FROM objects")
    for i in range(len(object_ids)):
        if object_ids[i][1] == "items":
            objects.append(Item(object_ids[i][0]))
        elif object_ids[i][1] == "players":
            objects.append(Player(object_ids[i][0]))

    bot.add_cog(General(bot))
    bot.add_cog(Admin(bot))
    bot.add_cog(Game(bot))


init()

print(os.getenv('TOKEN'))

bot.run(os.getenv('TOKEN'))
