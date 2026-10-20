#!/usr/bin/env python3
"""흰 배경 로고에서 발표용 변형 두 가지를 만든다.

블루 리포트의 표지·간지·마무리는 딥네이비(#071b45)와 다크(#101827)다.
회사 로고는 대개 흰 배경에 진한 색이라 그대로 올리면 흰 사각형이 생기고,
색도 배경에 묻힌다. 그래서 두 가지가 필요하다.

  <이름>-color.png          흰 배경을 투명으로 뺀 원색판 — 밝은 지면용
  <이름>-white.png          형태만 남긴 흰색 녹아웃 — 다크면용
  <이름>-symbol-white.png   국문 병기를 떼고 심볼만 남긴 녹아웃 — 다크면 워터마크용
  <이름>-symbol-color.png   같은 심볼의 원색판 — 밝은 지면 워터마크용

배경 워터마크는 심볼만 쓴다. 전체 로고를 720px 로 키우면 국문 병기까지 함께 커져
본문 괘선과 겹치고, 읽히지도 않으면서 자리만 차지한다. 우측 상단 마크는 작게 들어가
전체 로고가 그대로 읽히므로 거기서는 자르지 않는다.

로고가 두 가지 잉크(예: 파란 마크 + 검은 국문)로 되어 있으면 밝기 기준으로 알파를
잡을 수 없다. 한쪽이 항상 반투명해지기 때문이다. 그래서 흰색으로부터의 거리로
덮임(coverage)을 재고, 솔리드 잉크 기준은 중앙값으로 잡는다.

    python3 make_logo_variants.py logo.png
    python3 make_logo_variants.py logo.png --out-dir brand/ --name hct
"""
import argparse
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ensure_deps import need_pillow  # noqa: E402

need_pillow()                      # 없으면 여기서 알아서 받는다
from PIL import Image              # noqa: E402

WHITE_CUT = 240      # 이 값을 넘는 채널은 배경으로 본다
EDGE_CUT = 0.04      # 이보다 옅은 덮임은 버린다 (JPEG 노이즈 제거)


def dist_from_white(c):
    return math.sqrt(sum((255 - v) ** 2 for v in c))


def autocrop(im, pad=2):
    """흰 여백을 잘라낸다."""
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if not (r > WHITE_CUT and g > WHITE_CUT and b > WHITE_CUT):
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    if maxx < 0:
        sys.exit("오류: 흰색이 아닌 픽셀이 없다. 로고 이미지가 맞는지 확인한다.")
    return im.crop((max(0, minx - pad), max(0, miny - pad),
                    min(w, maxx + 1 + pad), min(h, maxy + 1 + pad)))


def split_symbol(alpha_img, min_gap=4):
    """국문 병기를 떼고 심볼만 남긴다.

    로고는 대개 [심볼] / 빈 띠 / [국문 병기] 구조다. 아래쪽 절반에서 가장 넓은
    빈 가로 띠를 찾아 그 위에서 자른다. 자를 자리를 못 찾으면 None 을 돌려주고
    호출한 쪽이 원본을 그대로 쓴다 — 심볼만 있는 로고도 있기 때문이다."""
    w, h = alpha_img.size
    a = alpha_img.split()[3]
    rows = [sum(a.getpixel((x, y)) for x in range(w)) for y in range(h)]
    top = max(rows) or 1
    blank = [i for i, v in enumerate(rows) if v / top < 0.02]

    # 아래쪽 절반에서만 찾는다. 심볼 안의 가로 여백에 걸리지 않게 한다.
    runs, cur = [], []
    for i in blank:
        if i < h * 0.45:
            continue
        if cur and i == cur[-1] + 1:
            cur.append(i)
        else:
            if len(cur) >= min_gap:
                runs.append(cur)
            cur = [i]
    if len(cur) >= min_gap:
        runs.append(cur)
    if not runs:
        return None

    gap = max(runs, key=len)
    # 띠 아래에 잉크가 남아 있어야 국문 병기다. 없으면 그냥 아래 여백이다.
    if not any(rows[y] / top >= 0.02 for y in range(gap[-1] + 1, h)):
        return None
    return alpha_img.crop((0, 0, w, gap[0])), (gap[0], gap[-1] + 1)


def build(path, out_dir, name):
    src = Image.open(path).convert("RGB")
    crop = autocrop(src)
    cw, ch = crop.size
    cp = crop.load()
    print(f"여백 제거: {src.size} → {crop.size}")

    ds = []
    for y in range(ch):
        for x in range(cw):
            d = dist_from_white(cp[x, y])
            if d > 12:
                ds.append(d)
    if not ds:
        sys.exit("오류: 잉크 픽셀을 찾지 못했다.")
    d_ink = statistics.median(ds)

    color = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); dc = color.load()
    white = Image.new("RGBA", (cw, ch), (255, 255, 255, 0)); dw = white.load()
    for y in range(ch):
        for x in range(cw):
            c = cp[x, y]
            a = dist_from_white(c) / d_ink
            a = 0.0 if a < EDGE_CUT else min(1.0, a)
            A = round(a * 255)
            dw[x, y] = (255, 255, 255, A)
            if A == 0:
                dc[x, y] = (0, 0, 0, 0)
            else:
                # 흰 배경과 합성되기 전의 순색을 역산해 가장자리 흰 테두리를 없앤다
                dc[x, y] = (*[max(0, min(255, round((v - 255 * (1 - a)) / a)))
                              for v in c], A)

    os.makedirs(out_dir, exist_ok=True)
    p_color = os.path.join(out_dir, f"{name}-color.png")
    p_white = os.path.join(out_dir, f"{name}-white.png")
    color.save(p_color); white.save(p_white)

    # 배경 워터마크용 — 국문 병기를 뗀 심볼만. 다크면·밝은면 두 벌을 낸다.
    sym = split_symbol(white)
    if sym:
        sym_img, (cut, resume) = sym
        p_sym = os.path.join(out_dir, f"{name}-symbol-white.png")
        sym_img.save(p_sym)
        # 같은 자리에서 원색판도 자른다. 자르는 위치는 알파 기준으로 이미 정해졌다.
        p_sym_color = os.path.join(out_dir, f"{name}-symbol-color.png")
        color.crop((0, 0, cw, cut)).save(p_sym_color)
        print(f"심볼 분리: {cut}행에서 자름 (국문은 {resume}행부터) → {sym_img.size}")
    else:
        p_sym = p_sym_color = None
        print("심볼 분리: 빈 띠를 못 찾았다. 심볼만 있는 로고로 보고 넘어간다.")

    ink = sum(1 for y in range(ch) for x in range(cw) if dw[x, y][3] > 0)
    opq = sum(1 for y in range(ch) for x in range(cw) if dw[x, y][3] == 255)
    print(f"잉크 픽셀 {ink} · 완전 불투명 {opq} ({opq/ink*100:.0f}%)")
    if opq / ink < 0.4:
        print("주의: 불투명 비율이 낮다. 원본이 흐리거나 옅은 로고일 수 있다. "
              "결과를 눈으로 확인한다.", file=sys.stderr)
    print(f"\n밝은 지면용: {p_color}")
    print(f"다크면용   : {p_white}")
    if p_sym:
        print(f"워터마크용 : {p_sym}   (brand.json 의 watermark)")
        print(f"           : {p_sym_color}   (brand.json 의 watermarkOnLight)")
    if ch < 120:
        print(f"\n주의: 원본 높이가 {ch}px다. 1920x1080 캔버스에서 64px로 쓰면 충분하지만, "
              f"인쇄나 확대에는 부족하다. 가능하면 SVG 원본을 받는다.", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="발표용 로고 변형 생성")
    ap.add_argument("logo", help="흰 배경 로고 이미지 (PNG·JPG)")
    ap.add_argument("--out-dir", default=".", help="출력 폴더 (기본 현재 폴더)")
    ap.add_argument("--name", help="출력 파일 이름 접두어 (기본 입력 파일명)")
    a = ap.parse_args()
    name = a.name or os.path.splitext(os.path.basename(a.logo))[0]
    build(a.logo, a.out_dir, name)


if __name__ == "__main__":
    main()
