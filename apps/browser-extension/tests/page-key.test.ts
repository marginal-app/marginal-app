import { describe, expect, it } from 'vitest';
import {
  canonicalizePageKey,
  pageIdentityFromPageKey,
  pageKeyFromHref,
  pageKeyFromLocation,
} from '@/utils/page-key';

describe('pageKey', () => {
  it('keeps query and drops hash', () => {
    expect(pageKeyFromHref('https://example.com/item?id=321#comments')).toBe(
      'https://example.com/item?id=321',
    );
  });

  it('treats different query values as different pages', () => {
    expect(pageKeyFromHref('https://example.com/item?id=321')).toBe(
      'https://example.com/item?id=321',
    );
    expect(pageKeyFromHref('https://example.com/item?id=322')).toBe(
      'https://example.com/item?id=322',
    );
  });

  it('matches origin + pathname when there is no query', () => {
    expect(pageKeyFromLocation({
      origin: 'https://example.com',
      pathname: '/hypothesis',
      search: '',
    })).toBe('https://example.com/hypothesis');
  });

  it('returns null for a non-URL href', () => {
    expect(pageKeyFromHref('not-a-url')).toBeNull();
  });

  it('splits a URL pageKey into origin, path, and query', () => {
    expect(pageIdentityFromPageKey('https://example.com/item?id=321#x')).toEqual({
      origin: 'https://example.com',
      path: '/item',
      query: '?id=321',
      pageKey: 'https://example.com/item?id=321',
    });
  });

  it('leaves a legacy non-URL pageKey as path', () => {
    expect(canonicalizePageKey('a')).toBe('a');
    expect(pageIdentityFromPageKey('a')).toEqual({
      origin: '',
      path: 'a',
      query: '',
      pageKey: 'a',
    });
  });
});
