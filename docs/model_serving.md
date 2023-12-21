## model serving

use `FastChat` for model serving, commands:

```bash
python3 -m fastchat.serve.controller --port 21005
CUDA_VISIBLE_DEVICES=0,1,2,3 python3 -u -m fastchat.serve.model_worker --model-names 'Baichuan-13B-Chat' --model-path 'Baichuan-13B-Chat' --num-gpus 4 --controller-address 'http://localhost:21005'
python3 -m fastchat.serve.openai_api_server --controller-address 'http://localhost:21005' --host 0.0.0.0 --port 28000
```

multi model work

```bash
python3 -m fastchat.serve.multi_model_worker --model-path Baichuan-13B-Chat --model-names Baichuan-13B-Chat --model-path llama-dl-hf13B/llama-13b --model-names llama-13b-hf --num-gpus 4 --controller-address 'http://localhost:21005'
```

test:

```bash
curl http://127.0.0.1:28000/v1/models
```