type IconProps = {
  className?: string;
  title?: string;
};

export function ArrowIcon({ className, title }: IconProps) {
  return (
    <svg
      aria-hidden={title ? undefined : true}
      className={className}
      role={title ? "img" : undefined}
      viewBox="0 0 24 24"
    >
      {title ? <title>{title}</title> : null}
      <path d="M4 12h15M14 7l5 5-5 5" fill="none" stroke="currentColor" strokeLinecap="square" />
    </svg>
  );
}

export function GridIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 18 18">
      <path
        d="M2.5 2.5h5v5h-5zM10.5 2.5h5v5h-5zM2.5 10.5h5v5h-5zM10.5 10.5h5v5h-5z"
        fill="none"
        stroke="currentColor"
      />
    </svg>
  );
}

export function ListIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 18 18">
      <path
        d="M2.5 3h1M6 3h9.5M2.5 9h1M6 9h9.5M2.5 15h1M6 15h9.5"
        fill="none"
        stroke="currentColor"
        strokeLinecap="square"
      />
    </svg>
  );
}

export function CloseIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 24 24">
      <path d="m5 5 14 14M19 5 5 19" fill="none" stroke="currentColor" />
    </svg>
  );
}

export function SearchIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 24 24">
      <circle cx="10.8" cy="10.8" fill="none" r="6.3" stroke="currentColor" />
      <path d="m15.5 15.5 4.2 4.2" fill="none" stroke="currentColor" />
    </svg>
  );
}

export function ThemeIcon({ className, mode }: IconProps & { mode: "system" | "light" | "dark" }) {
  if (mode === "dark") {
    return (
      <svg aria-hidden="true" className={className} viewBox="0 0 24 24">
        <path
          d="M20 15.2A8.4 8.4 0 0 1 8.8 4 8.5 8.5 0 1 0 20 15.2Z"
          fill="none"
          stroke="currentColor"
        />
      </svg>
    );
  }

  if (mode === "system") {
    return (
      <svg aria-hidden="true" className={className} viewBox="0 0 24 24">
        <rect fill="none" height="13" stroke="currentColor" width="18" x="3" y="4" />
        <path d="M8 21h8M12 17v4" fill="none" stroke="currentColor" />
      </svg>
    );
  }

  return (
    <svg aria-hidden="true" className={className} viewBox="0 0 24 24">
      <circle cx="12" cy="12" fill="none" r="4" stroke="currentColor" />
      <path
        d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9 7 7M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"
        fill="none"
        stroke="currentColor"
      />
    </svg>
  );
}
