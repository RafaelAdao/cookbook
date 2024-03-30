import logging

import apache_beam as beam
from apache_beam.io import ReadFromPubSub
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.core import DoFn
from google.cloud.bigtable.row import DirectRow
from google.cloud.bigtable.row_data import Cell
from apache_beam.io.gcp.bigtableio import WriteToBigTable

class ConvertToJson(beam.DoFn):
    def process(self, element):
        import json
        yield json.loads(element)

class MakeBigtableRow(DoFn):
    def process(self, element):
        row = DirectRow(row_key=str(element['id']))
        for key, value in element.items():
            row.set_cell(
                column_family_id='cf1',
                column=key,
                value=str(value)
            )
        yield row

def run():
    class ReadPubSubOptions(PipelineOptions):
        @classmethod
        def _add_argparse_args(cls, parser):
            parser.add_argument(
                "--subscription",
                required=True,
                help="PubSub subscription to read.",
            )
            parser.add_argument(
                "--project_id",
                required=True,
                help="Project ID"
            )
            parser.add_argument(
                "--instance_id",
                required=True,
                help="Cloud Bigtable instance ID"
            )
            parser.add_argument(
                "--table_id",
                required=True,
                help="Cloud Bigtable table ID"
            )
    options = ReadPubSubOptions(streaming=True)

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read PubSub subscription"
            >> ReadFromPubSub(subscription=options.subscription)
            | "Convert to JSON" >> beam.ParDo(ConvertToJson())
            | 'Map to Bigtable Row' >> beam.ParDo(MakeBigtableRow())
            | "Write to BigTable" >> WriteToBigTable(
                project_id=options.project_id,
                instance_id=options.instance_id,
                table_id=options.table_id
            )
            | beam.Map(logging.info)
        )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
