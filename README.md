# drift_correction

## プロジェクト概要

3Dイメージングのドリフト補正では、ソフトウェアの自動補正（Spatial Alignment: Automatic）を使うと大まかな補正は可能ですが、
空間的に似た領域が多いデータでは、基準位置の誤認識により補正値が急激に跳ね上がる場合があります。

このプロジェクトは、エクスポートしたドリフト値テキストをもとに、急激なズレを前後関係から補正して再利用しやすくするプログラムです。
ソフトウェア操作を含む業務全体の流れは [docs/manual.md](docs/manual.md) を参照してください。

## 環境構築の手順

プロジェクトルートで以下を実行します。

```bash
uv sync
```

## 実行方法

### 入力と出力

- 入力: `data/` に、ソフトウェアから `Text Format` で保存したドリフトデータを配置
- 設定: `config.yaml` で読み込むファイル名と閾値（異常なズレの検知用）を設定
- 出力: `output/YYYYmmdd_HHMMSS/` に補正後テキスト、グラフ画像、実行時の `config.yaml` を保存

### 実行コマンド

```bash
uv run python scripts/main.py
```

ステップ1（ソフトウェアからのエクスポート）とステップ4（Manual モードでの入力）の詳細は [docs/manual.md](docs/manual.md) を参照してください。

## 実験ノート

実行記録用に以下の表を利用してください。

| 日付 | データ | パラメータ（例: 閾値） | 出力フォルダ | 備考 |
|---|---|---|---|---|
| YYYY-MM-DD | Drift Profile for ... .txt | 閾値: 20 | output/YYYYmmdd_HHMMSS | |