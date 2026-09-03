export interface FooterLink {
  label: string;
  href: string;
}

export interface FooterGroup {
  title: string;
  links: FooterLink[];
}

export interface FooterColumn {
  groups: FooterGroup[];
}

export const footerColumns: FooterColumn[] = [
  {
    groups: [
      {
        title: 'Projects',
        links: [
          { label: 'All Projects', href: '/projects/' },
          { label: 'Interior Architecture', href: '/projects/interior-architecture/' },
          { label: 'Civil Engineering', href: '/projects/civil-engineering/' },
        ],
      },
    ],
  },

  {
    groups: [
      {
        title: 'About',
        links: [
          { label: 'Story', href: '/about/#introduction' },
          { label: 'Career Path', href: '/about/#experience' },
        ],
      },
    ],
  },
];
