class Runner:
    @staticmethod
    async def run(starting_agent, input):
        class Result:
            final_output = f"{starting_agent.name} received: {input}"
        return Result()
