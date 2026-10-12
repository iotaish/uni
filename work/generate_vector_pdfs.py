#!/usr/bin/env python3
"""Convert annotated waveform SVGs to high-fidelity vector PDFs.

Renders raw oscilloscope background photos with vector dimension lines,
cursor dashes, and annotation badges overlaid natively in PDF.
Extracts all tile layouts, metadata, and summary texts dynamically
from contact_sheet.html as the single source of truth (SSOT).
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import cv2
import matplotlib.font_manager as fm
import matplotlib.patches as patches
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class VectorLine:
    x1: float
    y1: float
    x2: float
    y2: float
    stroke: str
    stroke_width: float
    dash: str | None
    is_arrow: bool


@dataclass(frozen=True)
class AnnotationBadge:
    x: float
    y: float
    w: float
    h: float
    edge_color: str
    text: str


@dataclass(frozen=True)
class SvgScene:
    view_box: tuple[float, float, float, float]
    raw_filename: str
    lines: list[VectorLine]
    badges: list[AnnotationBadge]


@dataclass(frozen=True)
class TileConfig:
    name: str
    title: str


@dataclass(frozen=True)
class ContactSheetData:
    tiles: list[TileConfig]
    summary_title: str
    summary_text: str


class ContactSheetHtmlParser:
    """Extracts tile definitions and summary text directly from contact_sheet.html as SSOT."""

    @staticmethod
    def load(html_path: Path) -> ContactSheetData:
        if not html_path.exists():
            raise FileNotFoundError(f"Contact sheet HTML not found: {html_path}")

        content = html_path.read_text(encoding="utf-8")

        # 1. Waveform cards (01 to 14)
        wave_pattern = re.compile(
            r'<div class="card">\s*<div class="card-header">(.*?)</div>\s*<div class="card-body">\s*<object data="\.\./svg/(.*?)\.svg"',
            re.DOTALL,
        )
        matches = wave_pattern.findall(content)
        if not matches:
            raise ValueError(f"No valid waveform cards found in {html_path}")

        tiles = [TileConfig(name=name.strip(), title=title.strip()) for title, name in matches]

        # 2. Summary card (15)
        summary_pattern = re.compile(
            r'<div class="card card-summary">\s*<div class="card-header">(.*?)</div>\s*<div class="card-body card-summary-body"[^>]*>(.*?)</div>',
            re.DOTALL,
        )
        summary_match = summary_pattern.search(content)
        if summary_match:
            summary_title = summary_match.group(1).strip()
            summary_body = summary_match.group(2).strip()
            # Unescape basic HTML entities
            summary_body = (
                summary_body.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            )
            summary_text = f"{summary_title}\n\n{summary_body}"
        else:
            summary_title = "15 | 測定諸元一覧 ＆ アノテーション凡例"
            summary_text = summary_title

        return ContactSheetData(
            tiles=tiles,
            summary_title=summary_title,
            summary_text=summary_text,
        )


class SvgAnnotationParser:
    """Parses SVG vector elements and extracts drawing primitives."""

    def parse(self, svg_path: Path) -> SvgScene:
        tree = ET.parse(svg_path)
        root = tree.getroot()

        raw_vb = root.attrib.get("viewBox", "0 0 4000 3000").split()
        vx, vy, vw, vh = (float(v) for v in raw_vb)

        lines: list[VectorLine] = []
        badges: list[AnnotationBadge] = []
        raw_filename = ""

        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "image":
                href = elem.attrib.get("href", "")
                raw_filename = Path(href).name
            elif tag == "line":
                lines.append(self._parse_line(elem.attrib))
            elif tag == "g" and "transform" in elem.attrib:
                badge = self._parse_badge(elem)
                if badge is not None:
                    badges.append(badge)

        return SvgScene(
            view_box=(vx, vy, vw, vh),
            raw_filename=raw_filename,
            lines=lines,
            badges=badges,
        )

    def _parse_line(self, attr: dict[str, str]) -> VectorLine:
        return VectorLine(
            x1=float(attr["x1"]),
            y1=float(attr["y1"]),
            x2=float(attr["x2"]),
            y2=float(attr["y2"]),
            stroke=attr.get("stroke", "#FFFFFF"),
            stroke_width=float(attr.get("stroke-width", "3")),
            dash=attr.get("stroke-dasharray"),
            is_arrow="marker-start" in attr or "marker-end" in attr,
        )

    def _parse_badge(self, group: ET.Element) -> AnnotationBadge | None:
        transform = group.attrib.get("transform", "")
        if "translate" not in transform:
            return None

        coords_str = transform.replace("translate(", "").replace(")", "")
        parts = [p.strip() for p in coords_str.split(",")]
        if len(parts) < 2:
            return None
        tx, ty = float(parts[0]), float(parts[1])

        rect = group.find("{http://www.w3.org/2000/svg}rect")
        text = group.find("{http://www.w3.org/2000/svg}text")
        if rect is None or text is None or text.text is None:
            return None

        return AnnotationBadge(
            x=tx,
            y=ty,
            w=float(rect.attrib.get("width", "100")),
            h=float(rect.attrib.get("height", "50")),
            edge_color=rect.attrib.get("stroke", "#00E5FF"),
            text=text.text.strip(),
        )


class VectorPdfRenderer:
    """Renders background photos with vector annotations directly to PDF."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.svg_dir = base_dir / "svg"
        self.raw_dir = base_dir / "raw"
        self.contact_dir = base_dir / "contact_sheets"
        self.parser = SvgAnnotationParser()
        self.font_prop = self._load_japanese_font()
        self.sheet_data = ContactSheetHtmlParser.load(self.contact_dir / "contact_sheet.html")

    def _load_japanese_font(self) -> fm.FontProperties:
        candidate_paths = [
            Path("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"),
            Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
            Path("/Library/Fonts/Arial Unicode.ttf"),
        ]
        for path in candidate_paths:
            if path.exists():
                return fm.FontProperties(fname=str(path))
        return fm.FontProperties(family="sans-serif")

    def render_waveform_axis(
        self,
        ax: plt.Axes,
        name: str,
        *,
        show_header: bool = False,
        header_title: str = "",
    ) -> None:
        scene = self.parser.parse(self.svg_dir / f"{name}.svg")
        raw_image_path = self.raw_dir / scene.raw_filename
        vx, vy, vw, vh = scene.view_box

        img_bgr = cv2.imread(str(raw_image_path))
        if img_bgr is None:
            raise FileNotFoundError(f"Raw image not found: {raw_image_path}")
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        img_h, img_w, _ = img_rgb.shape
        ax.imshow(img_rgb, extent=[0, img_w, img_h, 0], aspect="auto")
        ax.set_xlim(vx, vx + vw)
        ax.set_ylim(vy + vh, vy)
        ax.axis("off")

        for line in scene.lines:
            if line.is_arrow:
                lw = line.stroke_width * 0.75
                ax.annotate(
                    "",
                    xy=(line.x2, line.y2),
                    xytext=(line.x1, line.y1),
                    arrowprops=dict(
                        arrowstyle="<|-|>,head_length=0.45,head_width=0.25",
                        color=line.stroke,
                        lw=lw,
                        shrinkA=0,
                        shrinkB=0,
                    ),
                )
            else:
                lw = line.stroke_width * 0.6
                ax.plot(
                    [line.x1, line.x2],
                    [line.y1, line.y2],
                    color=line.stroke,
                    lw=lw,
                    linestyle=(0, (6, 4)),
                    alpha=0.85,
                )

        for badge in scene.badges:
            cx = badge.x + badge.w / 2.0
            cy = badge.y + badge.h / 2.0
            bbox_props = dict(
                boxstyle="round,pad=0.25,rounding_size=0.4",
                fc="#0A0D12",
                ec=badge.edge_color,
                lw=1.2,
                alpha=0.92,
            )
            ax.text(
                cx,
                cy,
                badge.text,
                color="#FFFFFF",
                fontsize=9.5,
                fontweight="bold",
                ha="center",
                va="center",
                bbox=bbox_props,
            )

        if show_header:
            header_h = vh * 0.055
            rect = patches.Rectangle(
                (vx, vy),
                vw,
                header_h,
                linewidth=0,
                facecolor="#0D1117",
                alpha=0.92,
                zorder=10,
            )
            ax.add_patch(rect)
            ax.text(
                vx + vw * 0.02,
                vy + header_h * 0.62,
                header_title,
                color="#F0F6FC",
                fontsize=8.5,
                fontweight="bold",
                va="center",
                fontproperties=self.font_prop,
                zorder=11,
            )

    def generate_individual_pdfs(self) -> list[Path]:
        output_paths: list[Path] = []
        for tile in self.sheet_data.tiles:
            scene = self.parser.parse(self.svg_dir / f"{tile.name}.svg")
            _, _, vw, vh = scene.view_box

            fig_w = 8.0
            fig_h = 8.0 * (vh / vw)
            fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            self.render_waveform_axis(ax, tile.name, show_header=False)

            out_path = self.base_dir / f"{tile.name}.pdf"
            fig.savefig(out_path, format="pdf", dpi=150)
            plt.close(fig)
            output_paths.append(out_path)
        return output_paths

    def generate_contact_sheet_pdf(self) -> Path:
        cols, rows = 3, 5
        fig_w = 20.0
        fig_h = 20.0 * (rows / cols) * (2560 / 3820)
        fig, axes = plt.subplots(rows, cols, figsize=(fig_w, fig_h), dpi=150)
        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.015, hspace=0.02)

        for idx, tile in enumerate(self.sheet_data.tiles):
            r, c = divmod(idx, cols)
            self.render_waveform_axis(
                axes[r, c], tile.name, show_header=True, header_title=tile.title
            )

        # 15th tile: Render summary card parsed dynamically from HTML
        ax_summary = axes[4, 2]
        ax_summary.set_facecolor("#0D1117")
        ax_summary.axis("off")
        ax_summary.text(
            0.05,
            0.95,
            self.sheet_data.summary_text,
            color="#C9D1D9",
            fontsize=11,
            fontproperties=self.font_prop,
            va="top",
            ha="left",
            transform=ax_summary.transAxes,
            linespacing=1.6,
        )

        out_path = self.contact_dir / "sheet_all_15waveforms_annotated.pdf"
        fig.savefig(out_path, format="pdf", dpi=150)
        plt.close(fig)
        return out_path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    fig_dir = project_root / "report" / "fig_work_A"
    renderer = VectorPdfRenderer(fig_dir)

    print(f"Loaded {len(renderer.sheet_data.tiles)} tiles dynamically from contact_sheet.html.")
    print("Generating individual waveform vector PDFs...")
    indiv_pdfs = renderer.generate_individual_pdfs()
    print(f"Generated {len(indiv_pdfs)} individual PDFs.")

    print("Generating 15-waveform contact sheet vector PDF...")
    sheet_pdf = renderer.generate_contact_sheet_pdf()
    print(f"Generated contact sheet: {sheet_pdf}")


if __name__ == "__main__":
    main()
