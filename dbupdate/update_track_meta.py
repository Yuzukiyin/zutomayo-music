"""
增量更新脚本：为 tracks 表补充/修改 audio_url 与 lyrics,而无需重建数据库。

特性：
- 按 track_id 或 (album_title + track_title|track_number) 精确定位曲目
- 单条更新：通过命令行传入 --audio-url、--lyrics 或 --lyrics-file
- 批量更新：--json updates.json(示例见 updates_example.json)
- 默认 dry-run 只预览变更；加上 --apply 才会真正写入
- --show 可查看匹配到的曲目信息（不更新）

用法示例（Windows CMD）：
1) 仅查看某曲目（按 id）：
   python update_track_meta.py --id 42 --show

2) 单条更新（按 id，真正写入）：
   python update_track_meta.py --id 42 --audio-url "https://www.youtube.com/embed/xxxxx" --lyrics-file "lyrics\\秒針を噛む.txt" --apply

3) 单条更新（按专辑+曲名，先预览，未写入）：
   python update_track_meta.py --album-title "潜潜話" --track-title "正義" --audio-url "https://open.spotify.com/embed/track/xxxx" --dry-run

4) 批量更新（JSON，真正写入）：
   python update_track_meta.py --json updates.json --apply

注意：
- 数据库默认文件名为 music.db，脚本会在与本脚本相同目录查找。可通过 --db 指定路径。
- --lyrics 与 --lyrics-file 同时给出时，--lyrics-file 优先（从文件读取更安全，支持多行）。
- 请遵守版权：若没有授权，不要保存完整歌词；可改为空、短摘录或官方链接。
"""

from __future__ import annotations
import argparse
import json
import os
import sqlite3
from typing import Optional, Dict, Any, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(HERE, "music.db")


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def find_track_by_id(cur: sqlite3.Cursor, track_id: int) -> Optional[sqlite3.Row]:
    cur.execute(
        """
        SELECT t.*, a.title AS album_title
        FROM tracks t
        JOIN albums a ON a.id = t.album_id
        WHERE t.id = ?
        """,
        (track_id,),
    )
    return cur.fetchone()


def find_track_by_album_and_title(
    cur: sqlite3.Cursor,
    album_title: str,
    track_title: Optional[str] = None,
    track_number: Optional[int] = None,
) -> List[sqlite3.Row]:
    if track_title is None and track_number is None:
        raise ValueError("需要提供 track_title 或 track_number 其中之一")
    params: List[Any] = [album_title]
    where = ["a.title = ?"]
    if track_title is not None:
        where.append("t.title = ?")
        params.append(track_title)
    if track_number is not None:
        where.append("t.track_number = ?")
        params.append(track_number)
    sql = (
        "SELECT t.*, a.title AS album_title FROM tracks t JOIN albums a ON a.id = t.album_id "
        + "WHERE "
        + " AND ".join(where)
    )
    cur.execute(sql, params)
    return cur.fetchall()


def render_track_brief(row: sqlite3.Row) -> str:
    return (
        f"[id={row['id']}] {row['album_title']} - #{row['track_number']} "
        f"{row['title']} | duration={row['duration']}\n"
        f"    audio_url={row['audio_url']!r}\n"
        f"    lyrics={'<非空>' if row['lyrics'] else 'None'}"
    )


def update_track(
    cur: sqlite3.Cursor,
    track_id: int,
    audio_url: Optional[str] = None,
    lyrics: Optional[str] = None,
    apply: bool = False,
) -> Tuple[bool, str]:
    if audio_url is None and lyrics is None:
        return False, "未提供需要更新的字段（audio_url/lyrics 均为空）"

    sets: List[str] = []
    params: List[Any] = []
    if audio_url is not None:
        # 如果 audio_url 是列表/数组，转换为 JSON 字符串
        if isinstance(audio_url, list):
            audio_url_str = json.dumps(audio_url, ensure_ascii=False)
        else:
            audio_url_str = audio_url
        sets.append("audio_url = ?")
        params.append(audio_url_str)
    if lyrics is not None:
        sets.append("lyrics = ?")
        params.append(lyrics)
    params.append(track_id)

    sql = f"UPDATE tracks SET {', '.join(sets)} WHERE id = ?"
    if apply:
        cur.execute(sql, params)
        return True, f"已更新 track id={track_id}: {', '.join(sets)}"
    else:
        return False, f"DRY-RUN 预览 SQL: {sql} | params={params}"


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def handle_single(args: argparse.Namespace) -> int:
    db_path = args.db
    with connect(db_path) as conn:
        cur = conn.cursor()

        # 定位曲目
        row: Optional[sqlite3.Row] = None
        if args.id is not None:
            row = find_track_by_id(cur, int(args.id))
            if row is None:
                print(f"未找到 track id={args.id}")
                return 1
        else:
            matches = find_track_by_album_and_title(
                cur,
                album_title=args.album_title,
                track_title=args.track_title,
                track_number=int(args.track_number) if args.track_number is not None else None,
            )
            if not matches:
                print("未找到匹配曲目")
                return 1
            if len(matches) > 1:
                print("匹配到多条记录，请加上更精确的条件：")
                for m in matches:
                    print("  ", render_track_brief(m))
                return 2
            row = matches[0]

        if args.show:
            print(render_track_brief(row))
            return 0

        # 读取更新字段
        audio_url = args.audio_url
        lyrics: Optional[str] = None
        if args.lyrics_file:
            try:
                lyrics = read_text_file(os.path.join(HERE, args.lyrics_file) if not os.path.isabs(args.lyrics_file) else args.lyrics_file)
            except FileNotFoundError:
                print(f"歌词文件未找到: {args.lyrics_file}")
                return 1
        elif args.lyrics is not None:
            lyrics = args.lyrics

        changed, msg = update_track(
            cur,
            track_id=row["id"],
            audio_url=audio_url,
            lyrics=lyrics,
            apply=args.apply,
        )
        print(msg)
        if changed:
            conn.commit()
        return 0


def normalize_entry(e: Dict[str, Any]) -> Dict[str, Any]:
    # 支持多种键名；做一些宽松兼容
    mapping = {
        "id": ["id", "track_id"],
        "album_title": ["album_title", "album", "albumName"],
        "track_title": ["track_title", "title", "trackName"],
        "track_number": ["track_number", "number", "no"],
        "audio_url": ["audio_url", "audio", "url"],
        "lyrics": ["lyrics", "lyric", "text"],
        "lyrics_file": ["lyrics_file", "lyricsPath", "file"],
    }
    out: Dict[str, Any] = {}
    for key, aliases in mapping.items():
        for k in aliases:
            if k in e:
                out[key] = e[k]
                break
    return out


def handle_bulk(args: argparse.Namespace) -> int:
    db_path = args.db
    json_path = args.json
    if not os.path.isabs(json_path):
        json_path = os.path.join(HERE, json_path)

    if not os.path.exists(json_path):
        print(f"JSON 文件不存在: {json_path}")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("JSON 顶层必须是数组(list)")
        return 1

    success = 0
    skipped = 0
    failed = 0

    with connect(db_path) as conn:
        cur = conn.cursor()
        for idx, raw in enumerate(data, start=1):
            e = normalize_entry(raw)
            try:
                # 定位 track
                row: Optional[sqlite3.Row] = None
                if e.get("id") is not None:
                    row = find_track_by_id(cur, int(e["id"]))
                    if row is None:
                        print(f"[{idx}] 未找到 track id={e['id']}")
                        failed += 1
                        continue
                else:
                    album_title = e.get("album_title")
                    track_title = e.get("track_title")
                    track_number = int(e["track_number"]) if e.get("track_number") is not None else None
                    if not album_title or (track_title is None and track_number is None):
                        print(f"[{idx}] 条目缺少 album_title 以及 track_title/track_number 中至少一个，已跳过")
                        skipped += 1
                        continue
                    matches = find_track_by_album_and_title(cur, album_title, track_title, track_number)
                    if not matches:
                        print(f"[{idx}] 根据条件未找到曲目：album={album_title}, title={track_title}, number={track_number}")
                        failed += 1
                        continue
                    if len(matches) > 1:
                        print(f"[{idx}] 匹配到多条记录，需加更精确条件：")
                        for m in matches:
                            print("   ", render_track_brief(m))
                        failed += 1
                        continue
                    row = matches[0]

                # 读取要更新的字段
                audio_url = e.get("audio_url")
                lyrics = e.get("lyrics")
                lyrics_file = e.get("lyrics_file")
                if lyrics_file:
                    try:
                        lyrics_path = lyrics_file
                        if not os.path.isabs(lyrics_path):
                            lyrics_path = os.path.join(HERE, lyrics_path)
                        lyrics = read_text_file(lyrics_path)
                    except Exception as ex:
                        print(f"[{idx}] 读取歌词文件失败: {lyrics_file} - {ex}")
                        failed += 1
                        continue

                if audio_url is None and lyrics is None:
                    print(f"[{idx}] 未提供需要更新的字段，已跳过。{render_track_brief(row)}")
                    skipped += 1
                    continue

                changed, msg = update_track(cur, track_id=row["id"], audio_url=audio_url, lyrics=lyrics, apply=args.apply)
                print(f"[{idx}] {msg}")
                if changed:
                    success += 1
            except Exception as ex:
                print(f"[{idx}] 处理失败: {ex}")
                failed += 1
        if success and args.apply:
            conn.commit()

    print(f"完成：成功 {success}，跳过 {skipped}，失败 {failed}{'（已写入）' if args.apply else '（dry-run 预览）'}")
    return 0 if failed == 0 else 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="增量更新 tracks 的 audio_url 与 lyrics。默认 dry-run 预览，使用 --apply 写入。")
    p.add_argument("--db", default=DEFAULT_DB, help=f"数据库路径（默认：{DEFAULT_DB}）")
    p.add_argument("--apply", action="store_true", help="执行写入（默认不写，仅预览）")
    p.add_argument("--dry-run", action="store_true", help="强制预览（与默认一致，用于显式表达）")

    sub = p.add_subparsers(dest="mode", required=False)

    # 单条模式（默认）
    p.add_argument("--id", type=int, help="track id 直接定位")
    p.add_argument("--album-title", help="按专辑标题定位（需与 --track-title 或 --track-number 配合）")
    p.add_argument("--track-title", help="曲名定位")
    p.add_argument("--track-number", type=int, help="曲目序号定位")

    p.add_argument("--audio-url", help="要更新的外部播放器嵌入链接")
    p.add_argument("--lyrics", help="要更新的歌词文本（谨慎使用，注意版权）。若与 --lyrics-file 同时提供，歌词文件优先")
    p.add_argument("--lyrics-file", help="从文件读取歌词文本（UTF-8）")
    p.add_argument("--show", action="store_true", help="仅显示匹配曲目，不更新")

    # 批量 JSON 模式
    p.add_argument("--json", help="批量更新的 JSON 文件路径（顶层为数组）")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # 优先批量
    if args.json:
        return handle_bulk(args)

    # 单条：需要基本的定位条件
    if not args.show and not args.audio_url and not (args.lyrics or args.lyrics_file):
        print("未提供 --show 或任何更新字段（--audio-url/--lyrics/--lyrics-file），无事可做。\n"
              "可使用 --show 查看当前记录，或提供更新字段进行预览/写入。")
        return 1

    if args.id is None and not args.album_title:
        parser.error("请通过 --id 或 --album-title(+ --track-title/--track-number) 指定要操作的曲目。")

    return handle_single(args)


if __name__ == "__main__":
    raise SystemExit(main())
