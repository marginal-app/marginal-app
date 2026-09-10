import bookmarkUrl from '@/assets/icons/bookmark.svg?url';
import bookmarkFilledUrl from '@/assets/icons/bookmark-filled.svg?url';
import commentUrl from '@/assets/icons/comment.svg?url';
import openWebUrl from '@/assets/icons/open-web.svg?url';
import settingsUrl from '@/assets/icons/settings.svg?url';

type GlyphProps = {
  src: string;
  label?: string;
  size?: number;
};

function Glyph({ src, label = '', size = 16 }: GlyphProps) {
  return (
    <img
      src={src}
      alt={label}
      width={size}
      height={size}
      draggable={false}
    />
  );
}

export function CommentIcon() {
  return <Glyph src={commentUrl} />;
}

export function SettingsIcon() {
  return <Glyph src={settingsUrl} />;
}

export function BookmarkIcon({ filled = false }: { filled?: boolean }) {
  return <Glyph src={filled ? bookmarkFilledUrl : bookmarkUrl} />;
}

export function OpenWebIcon() {
  return <Glyph src={openWebUrl} />;
}
