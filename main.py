import keep_alive
from commands import *
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

if os.path.isdir("/home/runner"):  # Checks if running on a replit server, runs program to launch keep_alive if so
    keep_alive.keep_alive()
    bot.run(os.getenv('TOKEN'))
else:
    with open(".env", "r") as f:  # Had to use file management, since the os 'get env' didn't seem to work locally
        bot.run(f.read())
