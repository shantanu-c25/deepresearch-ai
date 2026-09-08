export function BrandMark({
  className = "h-5 w-5",
}: {
  className?: string;
}) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="9" cy="9" r="5.5" />
      <path d="M13 13 20 20" />
      <circle cx="9" cy="9" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="17.5" cy="15.5" r="1.5" fill="currentColor" stroke="none" />
      <path d="m13 9 3.5-2.5M13 12.5l3.5 2.5" />
    </svg>
  );
}
