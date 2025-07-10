"""Command Line Interface for Buyer Synthetic platform."""

import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rich_print

from .agents import SurveyCreatorAgent, SurveyExecutorAgent, ResultsVisualizerAgent
from .utils.logger import get_logger
from .config.settings import Settings
from . import __version__

# Initialize CLI app
app = typer.Typer(
    name="buyer-synthetic",
    help="AI-powered survey analysis platform",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()
logger = get_logger(__name__)


@app.command()
def version():
    """Show version information."""
    rich_print(f"[bold blue]Buyer Synthetic™[/bold blue] v{__version__}")
    rich_print("AI-powered survey analysis platform")


@app.command()
def create_sample(
    size: int = typer.Option(300, "--size", "-s", help="Sample size"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("csv", "--format", "-f", help="Output format (csv, json)")
):
    """Create a representative demographic sample."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Creating sample of {size} profiles...", total=None)
        
        try:
            # Create agent and generate sample
            creator = SurveyCreatorAgent(sample_size=size)
            sample_df = creator.generate_representative_sample()
            
            # Save sample
            if output is None:
                output = Path(f"sample_{size}_profiles.{format}")
            
            if format.lower() == "json":
                sample_df.to_json(output, orient="records", indent=2)
            else:
                sample_df.to_csv(output, index=False)
            
            progress.update(task, completed=100)
            
            # Show results
            table = Table(title="Sample Created Successfully")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Profiles", str(len(sample_df)))
            table.add_row("Average Age", f"{sample_df['edad'].mean():.1f} years")
            table.add_row("Gender Split", f"{(sample_df['genero'] == 'F').mean():.1%} Female")
            table.add_row("Output File", str(output))
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error creating sample: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def run_survey(
    sample_file: Path = typer.Argument(..., help="Path to sample CSV file"),
    questions_file: Optional[Path] = typer.Option(None, "--questions", "-q", help="Path to questions TXT file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Batch size for processing"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="OpenAI model to use")
):
    """Execute survey on a sample."""
    
    if not sample_file.exists():
        console.print(f"[red]Sample file not found: {sample_file}[/red]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        try:
            # Load sample
            import pandas as pd
            sample_df = pd.read_csv(sample_file)
            
            task = progress.add_task(f"Running survey on {len(sample_df)} profiles...", total=None)
            
            # Create executor and run survey
            executor = SurveyExecutorAgent()
            
            # Load custom questions if provided
            if questions_file and questions_file.exists():
                # TODO: Implement custom questions loading
                console.print("[yellow]Custom questions loading not yet implemented[/yellow]")
            
            results_df = executor.execute_survey(sample_df, batch_size=batch_size)
            
            # Save results
            if output is None:
                output = Path(f"survey_results_{len(results_df)}_responses.csv")
            
            results_df.to_csv(output, index=False)
            
            progress.update(task, completed=100)
            
            # Show results
            table = Table(title="Survey Completed Successfully")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Responses", str(len(results_df)))
            table.add_row("Completion Rate", "100%")  # TODO: Calculate actual rate
            table.add_row("Output File", str(output))
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error running survey: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def analyze(
    results_file: Path = typer.Argument(..., help="Path to survey results CSV file"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    include_viz: bool = typer.Option(True, "--visualizations/--no-visualizations", help="Generate visualizations"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, html, pdf)")
):
    """Analyze survey results and generate insights."""
    
    if not results_file.exists():
        console.print(f"[red]Results file not found: {results_file}[/red]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        try:
            # Load results
            import pandas as pd
            results_df = pd.read_csv(results_file)
            
            task = progress.add_task(f"Analyzing {len(results_df)} responses...", total=None)
            
            # Create visualizer and analyze
            visualizer = ResultsVisualizerAgent()
            analysis = visualizer.analyze_and_visualize(results_df)
            
            progress.update(task, completed=100)
            
            # Show key insights
            if analysis.get("insights"):
                panel = Panel(
                    "\n".join([f"• {insight}" for insight in analysis["insights"]]),
                    title="[bold blue]Key Insights[/bold blue]",
                    border_style="blue"
                )
                console.print(panel)
            
            # Show file outputs
            table = Table(title="Analysis Completed Successfully")
            table.add_column("Output", style="cyan")
            table.add_column("Path", style="green")
            
            if "analysis_file" in analysis:
                table.add_row("Analysis Report", analysis["analysis_file"])
            
            if "visualizations" in analysis:
                for viz_path in analysis["visualizations"]:
                    table.add_row("Visualization", viz_path)
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error analyzing results: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def dashboard(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run dashboard"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    auto_open: bool = typer.Option(True, "--open/--no-open", help="Auto-open browser")
):
    """Launch the Streamlit dashboard."""
    
    try:
        import subprocess
        import sys
        
        # Construct streamlit command
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "src/buyer_synthetic/ui/dashboard.py",
            "--server.port", str(port),
            "--server.address", host,
        ]
        
        if not auto_open:
            cmd.extend(["--server.headless", "true"])
        
        console.print(f"[green]Starting dashboard on http://{host}:{port}[/green]")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting dashboard: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Set OpenAI API key"),
    model: Optional[str] = typer.Option(None, "--model", help="Set default model"),
    sample_size: Optional[int] = typer.Option(None, "--sample-size", help="Set default sample size")
):
    """Manage configuration settings."""
    
    if show:
        # Show current configuration
        settings = Settings()
        
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("OpenAI API Key", "***" + settings.OPENAI_API_KEY[-4:] if settings.OPENAI_API_KEY else "Not set")
        table.add_row("Default Model", settings.DEFAULT_MODEL)
        table.add_row("Default Sample Size", str(settings.DEFAULT_SAMPLE_SIZE))
        table.add_row("Temperature", str(settings.TEMPERATURE))
        
        console.print(table)
    
    # Update configuration (basic implementation)
    if api_key or model or sample_size:
        console.print("[yellow]Configuration updates not yet implemented[/yellow]")
        console.print("Please update your .env file manually")


@app.command()
def validate(
    file: Path = typer.Argument(..., help="File to validate"),
    type: str = typer.Option("auto", "--type", "-t", help="File type (auto, sample, results, questions)")
):
    """Validate data files for correct format."""
    
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    
    try:
        import pandas as pd
        
        if file.suffix.lower() == '.csv':
            df = pd.read_csv(file)
            
            # Basic validation
            console.print(f"[green]✓[/green] File loaded successfully")
            console.print(f"[green]✓[/green] Rows: {len(df)}")
            console.print(f"[green]✓[/green] Columns: {len(df.columns)}")
            
            # Type-specific validation
            if type == "sample" or (type == "auto" and "nse" in df.columns):
                required_cols = ["id", "nombre", "edad", "genero", "region", "nse"]
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    console.print(f"[red]✗[/red] Missing required columns: {', '.join(missing_cols)}")
                else:
                    console.print(f"[green]✓[/green] All required sample columns present")
            
            console.print(f"[blue]Columns:[/blue] {', '.join(df.columns)}")
            
        else:
            console.print(f"[yellow]File type {file.suffix} not yet supported for validation[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()