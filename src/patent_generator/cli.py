"""
특허명세서 생성기 CLI
======================

커맨드 라인 인터페이스를 제공합니다.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from patent_generator.models.invention import InventionData
from patent_generator.generators.specification import PatentSpecificationGenerator
from patent_generator.templates.template_engine import TemplateEngine
from patent_generator.utils.validators import validate_invention_data, ValidationError
from patent_generator.utils.helpers import load_invention_file, create_sample_invention_data

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="patent-gen")
def main():
    """
    자동 특허명세서 작성 시스템

    발명자료(YAML/JSON)를 기반으로 한국 특허명세서를 자동 생성합니다.
    """
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    default=None,
    help="출력 파일 경로 (기본: 입력파일명_명세서.txt)",
)
@click.option(
    "-f", "--format",
    type=click.Choice(["txt", "md", "docx"]),
    default="txt",
    help="출력 형식 (기본: txt)",
)
@click.option(
    "--template",
    type=click.Path(exists=True),
    default=None,
    help="사용자 정의 템플릿 디렉토리",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="생성 전 데이터 검증 수행 (기본: 검증함)",
)
@click.option(
    "--stats/--no-stats",
    default=False,
    help="생성 후 통계 정보 출력",
)
def generate(input_file: str, output: str, format: str, template: str, validate: bool, stats: bool):
    """
    발명자료 파일에서 특허명세서 생성

    INPUT_FILE: 발명자료 파일 경로 (YAML 또는 JSON)
    """
    console.print(Panel.fit(
        "[bold blue]특허명세서 자동 생성 시스템[/bold blue]",
        border_style="blue",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # 1. 파일 로드
        task = progress.add_task("발명자료 로드 중...", total=None)
        try:
            invention_data = load_invention_file(input_file)
            progress.update(task, description="[green]발명자료 로드 완료[/green]")
        except Exception as e:
            console.print(f"[red]오류:[/red] 파일 로드 실패 - {e}")
            sys.exit(1)

        # 2. 데이터 검증
        if validate:
            progress.update(task, description="데이터 검증 중...")
            errors = validate_invention_data(invention_data)
            if errors:
                console.print("[yellow]검증 경고:[/yellow]")
                for error in errors:
                    console.print(f"  • {error}")
                if not click.confirm("경고가 있습니다. 계속 진행하시겠습니까?", default=True):
                    sys.exit(0)
            else:
                progress.update(task, description="[green]데이터 검증 완료[/green]")

        # 3. 명세서 생성
        progress.update(task, description="특허명세서 생성 중...")

        if template:
            # 템플릿 엔진 사용
            engine = TemplateEngine(template)
            spec_text = engine.render(invention_data)

            # 출력 파일 결정
            if output is None:
                input_path = Path(input_file)
                output = str(input_path.parent / f"{input_path.stem}_명세서.{format}")

            output_path = Path(output).with_suffix(f".{format}")
            output_path.write_text(spec_text, encoding="utf-8")
            saved_path = str(output_path)
        else:
            # 기본 생성기 사용
            generator = PatentSpecificationGenerator(invention_data)
            generator.generate()

            # 출력 파일 결정
            if output is None:
                input_path = Path(input_file)
                output = str(input_path.parent / f"{input_path.stem}_명세서")

            saved_path = generator.save(output, format=format)

        progress.update(task, description="[green]특허명세서 생성 완료[/green]")

    # 결과 출력
    console.print()
    console.print(f"[green]✓[/green] 명세서가 생성되었습니다: [bold]{saved_path}[/bold]")

    # 통계 출력
    if stats:
        if not template:
            stat_data = generator.get_statistics()
            _print_statistics(stat_data)


def _print_statistics(stats: dict):
    """통계 정보 테이블 출력"""
    table = Table(title="명세서 통계", show_header=True, header_style="bold cyan")
    table.add_column("항목", style="dim")
    table.add_column("값", justify="right")

    table.add_row("발명의 명칭", stats["title"])
    table.add_row("총 문자 수", f"{stats['total_characters']:,}")
    table.add_row("총 줄 수", f"{stats['total_lines']:,}")
    table.add_row("청구항 수", str(stats["num_claims"]))
    table.add_row("도면 수", str(stats["num_drawings"]))
    table.add_row("실시예 수", str(stats["num_embodiments"]))
    table.add_row("부호 수", str(stats["num_reference_signs"]))
    table.add_row("기술적 특징 수", str(stats["num_technical_features"]))
    table.add_row("효과 수", str(stats["num_effects"]))

    console.print()
    console.print(table)


@main.command()
@click.option(
    "-o", "--output",
    type=click.Path(),
    default="sample_invention.yaml",
    help="출력 파일 경로 (기본: sample_invention.yaml)",
)
@click.option(
    "-f", "--format",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="출력 형식 (기본: yaml)",
)
def sample(output: str, format: str):
    """
    예제 발명자료 파일 생성

    특허명세서 작성에 필요한 발명자료의 예제 파일을 생성합니다.
    """
    console.print("[cyan]예제 발명자료 생성 중...[/cyan]")

    sample_data = create_sample_invention_data()

    output_path = Path(output)
    if format == "yaml":
        output_path = output_path.with_suffix(".yaml")
        sample_data.to_yaml(str(output_path))
    else:
        output_path = output_path.with_suffix(".json")
        sample_data.to_json(str(output_path))

    console.print(f"[green]✓[/green] 예제 파일이 생성되었습니다: [bold]{output_path}[/bold]")
    console.print()
    console.print("[dim]이 파일을 수정하여 발명자료를 작성한 후,[/dim]")
    console.print("[dim]'patent-gen generate <파일>' 명령으로 명세서를 생성하세요.[/dim]")


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file: str):
    """
    발명자료 파일 검증

    발명자료 파일의 형식과 내용을 검증합니다.
    """
    console.print(f"[cyan]발명자료 검증 중: {input_file}[/cyan]")
    console.print()

    try:
        invention_data = load_invention_file(input_file)
    except Exception as e:
        console.print(f"[red]✗[/red] 파일 로드 실패: {e}")
        sys.exit(1)

    errors = validate_invention_data(invention_data)

    if errors:
        console.print("[yellow]검증 결과: 경고 발견[/yellow]")
        console.print()
        for i, error in enumerate(errors, 1):
            console.print(f"  {i}. {error}")
        console.print()
        console.print(f"[yellow]총 {len(errors)}건의 경고가 발견되었습니다.[/yellow]")
    else:
        console.print("[green]✓[/green] 검증 통과: 발명자료가 유효합니다.")

    # 기본 정보 출력
    console.print()
    console.print("[bold]발명자료 요약:[/bold]")
    console.print(f"  • 발명의 명칭: {invention_data.title}")
    console.print(f"  • 기술분야: {invention_data.technical_field.main_field}")
    console.print(f"  • 청구항 수: {len(invention_data.claims)}")
    console.print(f"  • 도면 수: {len(invention_data.drawings)}")
    console.print(f"  • 실시예 수: {len(invention_data.embodiments)}")


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
def info(input_file: str):
    """
    발명자료 파일 정보 출력

    발명자료 파일의 상세 정보를 보여줍니다.
    """
    try:
        invention_data = load_invention_file(input_file)
    except Exception as e:
        console.print(f"[red]오류:[/red] {e}")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold]{invention_data.title}[/bold]",
        title="발명의 명칭",
        border_style="blue",
    ))

    # 출원인/발명자 정보
    if invention_data.applicants:
        console.print("\n[bold cyan]출원인[/bold cyan]")
        for applicant in invention_data.applicants:
            console.print(f"  • {applicant.name} ({applicant.nationality})")

    if invention_data.inventors:
        console.print("\n[bold cyan]발명자[/bold cyan]")
        for inventor in invention_data.inventors:
            console.print(f"  • {inventor.name} ({inventor.nationality})")

    # 기술분야
    console.print("\n[bold cyan]기술분야[/bold cyan]")
    console.print(f"  • 주요: {invention_data.technical_field.main_field}")
    if invention_data.technical_field.sub_fields:
        console.print(f"  • 세부: {', '.join(invention_data.technical_field.sub_fields)}")
    if invention_data.technical_field.ipc_codes:
        console.print(f"  • IPC: {', '.join(invention_data.technical_field.ipc_codes)}")

    # 청구항 요약
    if invention_data.claims:
        console.print("\n[bold cyan]청구항 요약[/bold cyan]")
        independent = sum(1 for c in invention_data.claims if c.claim_type == "independent")
        dependent = sum(1 for c in invention_data.claims if c.claim_type == "dependent")
        console.print(f"  • 독립항: {independent}개")
        console.print(f"  • 종속항: {dependent}개")
        console.print(f"  • 총계: {len(invention_data.claims)}개")

    # 도면/실시예
    console.print("\n[bold cyan]도면 및 실시예[/bold cyan]")
    console.print(f"  • 도면: {len(invention_data.drawings)}개")
    console.print(f"  • 실시예: {len(invention_data.embodiments)}개")
    console.print(f"  • 부호: {len(invention_data.reference_signs)}개")


@main.command()
@click.option(
    "-o", "--output",
    type=click.Path(),
    default="templates",
    help="템플릿 저장 디렉토리 (기본: templates)",
)
def init_templates(output: str):
    """
    기본 템플릿 초기화

    사용자 정의 가능한 기본 템플릿을 생성합니다.
    """
    console.print("[cyan]템플릿 초기화 중...[/cyan]")

    engine = TemplateEngine(output)

    console.print(f"[green]✓[/green] 템플릿이 초기화되었습니다: [bold]{output}/[/bold]")
    console.print()
    console.print("[dim]생성된 템플릿 파일:[/dim]")
    for template in engine.list_templates():
        console.print(f"  • {template}")
    console.print()
    console.print("[dim]템플릿을 수정한 후 --template 옵션으로 사용하세요.[/dim]")


if __name__ == "__main__":
    main()
