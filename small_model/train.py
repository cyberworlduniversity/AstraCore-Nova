from __future__ import annotations

import argparse
from pathlib import Path
import torch
from torch.nn import functional as F
from .data import load_text_bytes, split_data, get_batch
from .model import NovaTiny


def main():
    parser = argparse.ArgumentParser(description="Train AstraCore Nova Tiny byte-level GRU")
    parser.add_argument("--data", default="data")
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seq-len", type=int, default=128)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--eval-every", type=int, default=100)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--out", default="checkpoints")
    args = parser.parse_args()

    torch.manual_seed(42)
    device = torch.device(args.device)
    corpus = load_text_bytes(args.data)
    train_data, val_data = split_data(corpus)
    model = NovaTiny().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    print(f"device={device} bytes={len(corpus)} parameters={model.parameter_count()}")

    best_val = float("inf")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for step in range(1, args.steps + 1):
        model.train()
        x, y = get_batch(train_data, args.batch_size, args.seq_len, device)
        logits, _ = model(x)
        loss = F.cross_entropy(logits.reshape(-1, 256), y.reshape(-1))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if step % args.eval_every == 0 or step == 1 or step == args.steps:
            model.eval()
            with torch.no_grad():
                vx, vy = get_batch(val_data, args.batch_size, args.seq_len, device)
                val_logits, _ = model(vx)
                val_loss = F.cross_entropy(val_logits.reshape(-1, 256), vy.reshape(-1)).item()
            print(f"step={step} train_loss={loss.item():.4f} val_loss={val_loss:.4f}")
            state = {"model": model.state_dict(), "step": step,
                     "config": {"vocab_size": 256, "embedding_dim": 64,
                                "hidden_size": 128, "num_layers": 4},
                     "val_loss": val_loss}
            torch.save(state, out / "latest.pt")
            if val_loss < best_val:
                best_val = val_loss
                torch.save(state, out / "best.pt")


if __name__ == "__main__":
    main()
