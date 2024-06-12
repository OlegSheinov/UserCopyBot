from api import client

fields = [
    "create",
]


async def send_vacancy(vacancy_text, channel):
    variables = {
        "fullVacancyText": vacancy_text,
        "channel": channel
    }
    query, query_name = await client.post_query(name_nutation="CreateVacancyMutation",
                                                name_query="createVacancy",
                                                fields=fields, variables=variables)
    response = await client.execute(query, query_name, variables)
    return response
