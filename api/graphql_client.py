import os

import aiohttp


class GraphQLClient:

    async def post_query(self, name_nutation: str, name_query: str, fields: list, variables: dict = None):
        if variables:

            mutation_variables_types = ", ".join(f'${key}: String!' for key in variables.keys())
            mutation_variables = ", ".join(f"{key}: ${key}" for key in variables.keys())
        else:
            mutation_variables_types = None
            mutation_variables = None
        query = \
            f"""
            mutation {name_nutation} ({mutation_variables_types}) {{
                {name_query} ({mutation_variables}) {{
                    {' '.join(fields)}
                }}
            }}    
            """
        return query, name_query

    async def execute(self, query, name_query: str = None, variables: dict = None):
        query = {'query': query, "variables": variables}
        async with aiohttp.ClientSession() as session:
            async with session.post(os.getenv("API_URL"), json=query) as resp:
                response = await resp.json()
                return response['data'][name_query]
