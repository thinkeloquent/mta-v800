import pytest
import json
import os
import asyncio
from runtime_template_resolver import create_resolver, create_registry, ComputeScope, ResolveError

FIXTURES_PATH = os.path.join(os.path.dirname(__file__), '../../__fixtures__/test_vectors.json')

def load_vectors():
    with open(FIXTURES_PATH) as f:
        data = json.load(f)
    return data['vectors']

@pytest.mark.asyncio
@pytest.mark.parametrize("vector", load_vectors())
async def test_vectors(vector):
    registry = create_registry()
    
    # Setup mock function if needed
    if vector.get('setup'):
        setup = vector['setup']
        fn_name = setup['fn']
        ret_val = setup['returns']
        # Register async function
        async def mock_fn(ctx=None):
            return ret_val
        registry.register(fn_name, mock_fn, ComputeScope.REQUEST)

    resolver = create_resolver(registry=registry)
    
    context = vector['context']
    expression = vector['expression']
    
    # Run test
    if vector.get('expected_error'):
        # Check matching error code
        with pytest.raises(ResolveError) as excinfo:
             if vector.get('depth'):
                 await resolver.resolve(expression, context, depth=vector['depth'])
             else:
                 await resolver.resolve(expression, context)
        assert excinfo.value.code == vector['expected_error']
    else:
        result = await resolver.resolve(expression, context)
        assert result == vector['expected_resolve']
