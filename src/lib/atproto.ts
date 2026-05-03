const publicResolver = 'https://public.api.bsky.app';
const plcDirectory = 'https://plc.directory';

type DidDocument = {
  service?: Array<{
    id?: string;
    serviceEndpoint?: string;
  }>;
};

export type AtprotoRecord = Record<string, unknown>;

export type AtprotoPostRecord = AtprotoRecord & {
  text?: string;
  createdAt?: string;
  reply?: unknown;
};

export type AtprotoListRecord<TRecord extends AtprotoRecord = AtprotoRecord> = {
  uri: string;
  value: TRecord;
};

type ListRecordsResponse<TRecord extends AtprotoRecord> = {
  records?: AtprotoListRecord<TRecord>[];
};

export async function resolveDid(handle: string): Promise<string> {
  const cacheKey = `bsky-did:${handle}`;
  const cached = sessionStorage.getItem(cacheKey);

  if (cached) {
    return cached;
  }

  const response = await fetch(
    `${publicResolver}/xrpc/com.atproto.identity.resolveHandle?handle=${encodeURIComponent(handle)}`,
  );

  if (!response.ok) {
    throw new Error('Could not resolve Bluesky handle.');
  }

  const body = (await response.json()) as { did?: string };

  if (!body.did) {
    throw new Error('Bluesky handle did not return a DID.');
  }

  sessionStorage.setItem(cacheKey, body.did);
  return body.did;
}

export async function resolvePds(did: string): Promise<string> {
  const cacheKey = `bsky-pds:${did}`;
  const cached = sessionStorage.getItem(cacheKey);

  if (cached) {
    return cached;
  }

  const response = await fetch(`${plcDirectory}/${did}`);

  if (!response.ok) {
    throw new Error('Could not resolve ATproto PDS.');
  }

  const didDocument = (await response.json()) as DidDocument;
  const pdsService = didDocument.service?.find(({ id }) => id === '#atproto_pds');

  if (!pdsService?.serviceEndpoint) {
    throw new Error('DID document did not include a PDS endpoint.');
  }

  sessionStorage.setItem(cacheKey, pdsService.serviceEndpoint);
  return pdsService.serviceEndpoint;
}

export async function listRecords<TRecord extends AtprotoRecord = AtprotoRecord>({
  collection,
  limit,
  repo,
  serviceEndpoint,
}: {
  collection: string;
  limit: number;
  repo: string;
  serviceEndpoint: string;
}): Promise<AtprotoListRecord<TRecord>[]> {
  const response = await fetch(
    `${serviceEndpoint}/xrpc/com.atproto.repo.listRecords?repo=${encodeURIComponent(repo)}&collection=${encodeURIComponent(collection)}&limit=${limit}`,
  );

  if (!response.ok) {
    throw new Error('Could not load records from the PDS.');
  }

  const body = (await response.json()) as ListRecordsResponse<TRecord>;
  return body.records ?? [];
}

export async function listPostRecords({
  handle,
  limit = 50,
}: {
  handle: string;
  limit?: number;
}): Promise<{ did: string; records: AtprotoListRecord<AtprotoPostRecord>[] }> {
  const did = await resolveDid(handle);
  const pds = await resolvePds(did);
  const records = await listRecords<AtprotoPostRecord>({
    collection: 'app.bsky.feed.post',
    limit,
    repo: did,
    serviceEndpoint: pds,
  });

  return { did, records };
}

export function createBskyPostLink({
  fallbackHandle,
  did,
  uri,
}: {
  fallbackHandle: string;
  did: string;
  uri: string;
}): string {
  const recordKey = uri.split('/').at(-1);

  if (!recordKey) {
    return `https://bsky.app/profile/${fallbackHandle}`;
  }

  return `https://bsky.app/profile/${did}/post/${recordKey}`;
}
