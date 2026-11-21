from __future__ import annotations

import argparse
import torch
from .model import NovaTiny


def main():
    parser = argparse.ArgumentParser(description="Generate text with Nova Tiny")
    parser.add_argument("--checkpoint", default="checkpoints/best.pt")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--max-new-bytes", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    device = torch.device(args.device)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = NovaTiny(**checkpoint.get("config", {})).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    prompt_bytes = args.prompt.encode("utf-8")
    if not prompt_bytes:
        prompt_bytes = b" "
    prompt = torch.tensor(list(prompt_bytes), dtype=torch.long, device=device)
    generated = prompt.unsqueeze(0)
    hidden = None
    with torch.no_grad():
        logits, hidden = model(prompt.unsqueeze(0), hidden)
        for _ in range(args.max_new_bytes):
            next_logits = logits[:, -1, :] / max(args.temperature, 1e-5)
            next_byte = torch.multinomial(torch.softmax(next_logits, dim=-1), 1)
            generated = torch.cat((generated, next_byte), dim=1)
            logits, hidden = model(next_byte, hidden)

    text = generated[0].cpu().numpy().tobytes().decode("utf-8", errors="replace")
    print(text)


if __name__ == "__main__":
    main()
