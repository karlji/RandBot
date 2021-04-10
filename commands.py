import random
import json
import asyncio
import pymongo
import messages as mes
import tokens as tok

clientDB = pymongo.MongoClient(tok.mongo_token)
db = clientDB.bot
collection = db.lists


# Base class for other exceptions
class Error(Exception):
    pass


# Raised when the list format is wrong
class ListFormatError(Error):
    pass


async def list_command(client, message):
    list_name = message.content.replace('?list ', '')
    title = "Creating list: " + list_name
    await message.channel.send(embed=mes.list_message(title))

    try:
        def check(m):
            if m.content.find(";") != -1:
                return True
            else:
                raise ListFormatError

        message = await client.wait_for('message', timeout=60.0, check=check)

    except asyncio.TimeoutError:
        await message.channel.send(embed=mes.timeout_message())
    except ListFormatError:
        await message.channel.send(embed=mes.format_error_message())

    else:
        server_name = message.guild.name
        full_user = message.author.name + "#" + message.author.discriminator
        collection.insert_one({"Server": server_name,
                               "User": full_user,
                               "List_Name": list_name, "List": message.content})
        title = list_name + " created!"
        await message.channel.send(embed=mes.list_created_message(title))
    return


async def random_command(message):
    list_name = message.content.replace('?random ', '')
    server_name = message.guild.name
    full_user = message.author.name + "#" + message.author.discriminator
    item = randomize(server_name, full_user, list_name)
    await message.channel.send(embed=mes.random_message(item))
    return


async def delete_command(message):
    list_name = message.content.replace('?delete ', '')
    server_name = message.guild.name
    full_user = message.author.name + "#" + message.author.discriminator
    collection.delete_one({"Server": server_name,
                           "User": full_user,
                           "List_Name": list_name})
    title = list_name + " deleted!"
    await message.channel.send(embed=mes.delete_message(title))
    return


async def commands_command(message):
    await message.channel.send(embed=mes.commands_message())
    return


def randomize(server_name, full_user, list_name):
    output = collection.find_one({"Server": server_name,
                                  "User": full_user,
                                  "List_Name": list_name},
                                 {"List": 1, "_id": False})
    output = json.dumps(output)
    output = output.replace('{"List": "', '')
    output = output.replace('"}', '')
    output = output.split(";")
    output = random.choice(tuple(output))
    if output == "null":
        output = "List not found!"
    return output
