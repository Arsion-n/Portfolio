export interface NavChild {
  label: string;
  href: string;
}

export interface NavGroup {
  heading: string;
  elevated?: boolean;
  items: NavChild[];
}

export interface NavItem {
  label: string;
  href: string;
  groups?: NavGroup[];
}

export const navItems: NavItem[] = [
  { label: 'Home', href: '/' },
  {
    label: 'Projects',
    href: '/projects/',
    groups: [
      {
        heading: 'Projects',
        elevated: true,
        items: [
          { label: 'Project A', href: '/projects/project-a/' },
          { label: 'Project B', href: '/projects/project-b/' },
          { label: 'Project C', href: '/projects/project-c/' },
        ],
      },
    ],
  },
  {
    label: 'About',
    href: '/about/',
    groups: [
      {
        heading: 'About Me',
        elevated: true,
        items: [
          { label: 'Introduction', href: '/about/#introduction' },
          { label: 'Experience', href: '/about/#experience' },
          { label: 'Skills', href: '/about/#skills' },
        ],
      },
      {
        heading: 'Quick Links',
        items: [
          { label: 'CV Download', href: '/about/cv/' },
        ],
      },
    ],
  },
];

/** Flatten all group items for a nav item (useful for mobile) */
export function getFlatChildren(item: NavItem): NavChild[] {
  return item.groups?.flatMap(g => g.items) ?? [];
}
