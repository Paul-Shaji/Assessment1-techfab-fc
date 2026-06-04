import { Loader2 } from "lucide-react";

export function Spinner({ size = 20 }: { size?: number }) {
  return <Loader2 className="animate-spin text-brand-600" size={size} />;
}

export function FullPageSpinner({ label }: { label?: string }) {
  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-3 text-slate-500">
      <Loader2 className="animate-spin text-brand-600" size={32} />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}
