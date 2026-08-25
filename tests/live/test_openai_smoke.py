
import os
import pytest
from app.infrastructure.llm.openai import OpenAILLMProvider
from tests.support.fixtures import seller_food

pytestmark=pytest.mark.live

@pytest.mark.asyncio
async def test_real_openai_structured_recipe_smoke():
    if os.getenv('RUN_OPENAI_LIVE')!='1':
        pytest.skip('Set RUN_OPENAI_LIVE=1 and OPENAI_API_KEY to make a paid live API call')
    provider=OpenAILLMProvider(api_key=os.environ['OPENAI_API_KEY'],model=os.getenv('OPENAI_MODEL','gpt-5.6'))
    result=await provider.generate_seller_recipe(food=seller_food(),language='en')
    assert result.title
    assert result.steps
