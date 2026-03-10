import asyncio
import time
import argparse
import json
from openai import AsyncOpenAI
import statistics

async def profile_request(client, model, prompt, request_id):
    """
    Sends a single request to the vLLM endpoint and measures:
    - Time To First Token (TTFT)
    - Inter-Token Latency (ITL)
    - Total tokens and Tokens Per Second (TPS)
    """
    start_time = time.perf_counter()
    first_token_time = None
    
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=1024,
            temperature=0.0
        )
        
        tokens_received = 0
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                tokens_received += 1
                
        end_time = time.perf_counter()
        
        if first_token_time is None:
            first_token_time = end_time # fallback if no tokens
            
        ttft = first_token_time - start_time
        total_time = end_time - start_time
        generation_time = end_time - first_token_time
        
        tps = (tokens_received - 1) / generation_time if generation_time > 0 else 0
        itl = generation_time / (tokens_received - 1) if tokens_received > 1 else 0
        
        return {
            "request_id": request_id,
            "ttft_sec": ttft,
            "itl_sec": itl,
            "tps": tps,
            "total_time_sec": total_time,
            "tokens": tokens_received,
            "success": True
        }
        
    except Exception as e:
        print(f"Request {request_id} failed: {e}")
        return {
            "request_id": request_id,
            "success": False,
            "error": str(e)
        }

async def run_benchmark(base_url, api_key, model, prompt, concurrency, num_requests):
    """
    Runs multiple concurrent requests to profile the vLLM server.
    """
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    print(f"Starting vLLM benchmark...")
    print(f"Endpoint: {base_url}")
    print(f"Model: {model}")
    print(f"Concurrency: {concurrency}, Total Requests: {num_requests}\n")
    
    semaphore = asyncio.Semaphore(concurrency)
    
    async def bound_request(req_id):
        async with semaphore:
            return await profile_request(client, model, prompt, req_id)
            
    start_time = time.perf_counter()
    
    tasks = [bound_request(i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    total_benchmark_time = end_time - start_time
    
    # Analyze results
    successful_results = [r for r in results if r["success"]]
    failed_count = len(results) - len(successful_results)
    
    if not successful_results:
        print("All requests failed!")
        return
        
    ttfts = [r["ttft_sec"] for r in successful_results]
    tps_list = [r["tps"] for r in successful_results]
    itls = [r["itl_sec"] for r in successful_results]
    total_tokens = sum(r["tokens"] for r in successful_results)
    
    print("="*40)
    print("BENCHMARK RESULTS")
    print("="*40)
    print(f"Total time taken:      {total_benchmark_time:.2f}s")
    print(f"Total requests:        {num_requests}")
    print(f"Successful requests:   {len(successful_results)}")
    print(f"Failed requests:       {failed_count}")
    print(f"Total tokens gen:      {total_tokens}")
    print(f"Overall throughput:    {total_tokens/total_benchmark_time:.2f} tokens/sec")
    print("-" * 40)
    
    print("Time To First Token (TTFT):")
    print(f"  Mean:   {statistics.mean(ttfts):.3f}s")
    print(f"  Median: {statistics.median(ttfts):.3f}s")
    print(f"  Max:    {max(ttfts):.3f}s")
    print(f"  Min:    {min(ttfts):.3f}s")
    
    print("\nTokens Per Second (TPS) per stream:")
    print(f"  Mean:   {statistics.mean(tps_list):.1f}")
    print(f"  Max:    {max(tps_list):.1f}")
    print(f"  Min:    {min(tps_list):.1f}")
    
    print("\nInter-Token Latency (ITL):")
    print(f"  Mean:   {statistics.mean(itls)*1000:.1f}ms")
    print(f"  Median: {statistics.median(itls)*1000:.1f}ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vLLM Performance Profiler")
    parser.add_argument("--url", default="http://localhost:8000/v1", help="vLLM API base URL")
    parser.add_argument("--key", default="EMPTY", help="API Key")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--prompt", default="Explain the theory of relativity in exactly 3 short paragraphs.", help="Test prompt")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of parallel requests")
    parser.add_argument("--requests", type=int, default=5, help="Total number of requests to send")
    
    args = parser.parse_args()
    
    asyncio.run(run_benchmark(
        base_url=args.url,
        api_key=args.key,
        model=args.model,
        prompt=args.prompt,
        concurrency=args.concurrency,
        num_requests=args.requests
    ))
