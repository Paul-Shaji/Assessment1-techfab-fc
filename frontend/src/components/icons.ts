import {
  ShoppingCart,
  Package,
  Loader,
  CheckCircle2,
  Users,
  Award,
  type LucideIcon,
} from "lucide-react";

// Maps the icon string returned by get_dashboard_stats to a lucide component.
const ICONS: Record<string, LucideIcon> = {
  "shopping-cart": ShoppingCart,
  package: Package,
  loader: Loader,
  "check-circle": CheckCircle2,
  users: Users,
  award: Award,
};

export function iconFor(name: string): LucideIcon {
  return ICONS[name] ?? Package;
}
