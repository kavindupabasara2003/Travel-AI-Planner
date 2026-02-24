-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your travel destinations
create table destinations (
  id bigint primary key generated always as identity,
  location_name text not null,
  located_city text,
  location_address text,
  location_type text,
  avg_rating numeric,
  ai_context text, -- Validated context string for RAG
  embedding vector(1536) -- OpenAI text-embedding-3-small generates 1536 dimensions
);

-- Create a function to search for destinations
create or replace function match_destinations (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  location_name text,
  located_city text,
  location_type text,
  ai_context text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    destinations.id,
    destinations.location_name,
    destinations.located_city,
    destinations.location_type,
    destinations.ai_context,
    1 - (destinations.embedding <=> query_embedding) as similarity
  from destinations
  where 1 - (destinations.embedding <=> query_embedding) > match_threshold
  order by destinations.embedding <=> query_embedding
  limit match_count;
end;
$$;
