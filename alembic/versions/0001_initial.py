"""initial ai tables and pgvector extension"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.create_table('ai_generation_runs',
        sa.Column('generation_id',sa.String(64),primary_key=True),
        sa.Column('user_id',sa.String(36),nullable=False),
        sa.Column('feature',sa.String(64),nullable=False),
        sa.Column('model',sa.String(128),nullable=False),
        sa.Column('prompt_version',sa.String(32),nullable=False),
        sa.Column('status',sa.String(32),nullable=False),
        sa.Column('metadata_json',sa.JSON(),nullable=False),
        sa.Column('output_json',sa.JSON(),nullable=True),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index('ix_ai_generation_runs_user_id','ai_generation_runs',['user_id'])
    op.create_index('ix_ai_generation_runs_feature','ai_generation_runs',['feature'])
    op.create_index('ix_ai_generation_runs_status','ai_generation_runs',['status'])
    op.create_table('recommendation_events',
        sa.Column('id',sa.Integer(),primary_key=True,autoincrement=True),
        sa.Column('user_id',sa.String(36),nullable=False),
        sa.Column('recommendation_id',sa.String(64),nullable=False),
        sa.Column('item_type',sa.String(32),nullable=False),
        sa.Column('item_id',sa.String(64),nullable=False),
        sa.Column('event',sa.String(32),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index('ix_rec_event_user_created','recommendation_events',['user_id','created_at'])
    op.create_table('embedding_records',
        sa.Column('resource_key',sa.String(128),primary_key=True),
        sa.Column('resource_type',sa.String(32),nullable=False),
        sa.Column('model',sa.String(128),nullable=False),
        sa.Column('embedding_json',sa.JSON(),nullable=False),
        sa.Column('content_hash',sa.String(64),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
    )
    # Native vector store reserved for recommendation evolution without adding a new DB service.
    op.execute('ALTER TABLE embedding_records ADD COLUMN IF NOT EXISTS embedding vector(1536)')

def downgrade():
    op.drop_table('embedding_records'); op.drop_table('recommendation_events'); op.drop_table('ai_generation_runs')
