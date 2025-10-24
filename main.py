import fire
from core import get_model_metadata

if __name__ == '__main__':
 fire.Fire({
      'get_model_metadata': get_model_metadata
  })
