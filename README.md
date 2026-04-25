# drift_correction

## 1. Description

このプロジェクトは、講義のベストプラクティス（再現可能な研究の原則と実験管理）に準拠して作成された、実験データ（ABFGrabber 等）のドリフト補正パイプラインです。

主な目的は、実験データ中の X/Y ドリフトを検出し、区間ごとの不連続を線形補正することです。

処理の流れ:

1. 入力データ（X, Y）を読み込む
2. しきい値に基づいてジャンプ点を検出し区間分割する
3. 直前区間の線形モデルを使って不連続を補正する
4. 補正後データと可視化図を保存する

チーム運用の前提:

- 設定値は `config.yaml` で管理し、実行時に出力フォルダへコピーして履歴化する
- 実行結果はタイムスタンプ付きフォルダに分離して保存する
- 実験ログ表に「入力・閾値・保存先」を残し、後追い可能にする

## 2. Setup

このプロジェクトではパッケージ管理に `uv` を使用します（推奨）。

再現可能な環境を構築するため、プロジェクトルートで以下を実行してください。

```bash
uv sync
```

最短実行（初回セットアップから実行まで）:

```bash
uv sync
uv run python scripts/main.py
```

補足:

- `uv sync` は `pyproject.toml` と `uv.lock` に基づいて依存関係を同期します。
- これにより他の実行者でも同じ環境を再現しやすくなります。

チーム運用ルール:

- 依存を追加・更新したら `uv lock` を更新し、差分をコミットする
- 実行環境差異を減らすため、実行コマンドは `uv run ...` を使う

## 3. Usage

### ディレクトリ構成（主要部分）

```text
drift_correction/
├─ config.yaml
├─ data/                     # 入力データ
├─ output/                   # 実行ごとの結果保存先
├─ scripts/
│  └─ main.py                # 実行スクリプト
└─ src/
   └─ drift_correction/
      ├─ __init__.py
      └─ processor.py        # 補正ロジック本体
```

### 実行手順

1. `config.yaml` で入力ファイルや閾値パラメータ（`x_threshold`, `y_threshold`）を調整する
2. プロジェクトルートで以下を実行する

```bash
uv run python scripts/main.py
```

3. 結果は `output/YYYYmmdd_HHMMSS/` に保存される
4. 結果フォルダには補正済みテキスト、プロット画像、実行時の `config.yaml` が含まれる

### 運用時の注意

- `data/` には入力元データのみを置く（加工後データは置かない）
- `output/` は成果物置き場として扱い、実行ごとに新規サブディレクトリを作る
- `config.yaml` を変更して再実行した場合は、実験ログ表に必ず追記する

### よくあるエラー

- `Input file not found`:
	- `config.yaml` の `paths.input_dir` と `files.input` の組み合わせを確認
- `Input file must contain at least two rows`:
	- 入力ファイル形式（最低2行: X/Y）を確認
- どの結果が最新か分からない:
	- `output/` の最新タイムスタンプフォルダを確認し、実験ログ表と対応付ける

## 4. Experiment Log

「どのデータに対して、どの閾値で実行し、どのフォルダに結果が保存されたか」を追跡するため、以下の表を実験ノートとして利用してください。

| 日付 | 入力データ | 閾値(X, Y) | 結果フォルダ | 備考 |
|---|---|---|---|---|
| 2026-04-25 | Drift Profile for Frame Grabber 100 frames_3_20M_P8.txt | (20.0, 10.0) | output/20260425_172914 | 初期実行 |
| YYYY-MM-DD | <data file> | (<x_threshold>, <y_threshold>) | output/<timestamp> | <notes> |

記入ルール（引き継ぎ用）:

- 1実行につき1行を追加する
- 同じ入力データでも、閾値を変えたら別行にする
- 備考には「目的」「異常値の有無」「次回改善点」を短く残す

---

### Handover Checklist

- 実行前に `uv sync` を実施した
- `config.yaml` の入力ファイル名と閾値を確認した
- 実行後に `output/<timestamp>/` の生成を確認した
- 実験ログ表を更新した