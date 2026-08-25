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
      {
        title: 'Portfolio',
        links: [
          { label: 'Case Studies', href: '/projects/' },
          { label: 'Design Notes', href: '/projects/' },
        ],
      },
    ],
  },
  {
    groups: [
      {
        title: 'Account',
        links: [
          { label: 'About Me', href: '/about/' },
          { label: 'CV (Coming Soon)', href: '/about/' },
        ],
      },
      {
        title: 'Updates',
        links: [
          { label: 'Latest News (Soon)', href: '/' },
          { label: 'Announcements (Soon)', href: '/' },
        ],
      },
    ],
  },
  {
    groups: [
      {
        title: 'Studio',
        links: [
          { label: 'Contact', href: '#site-footer' },
          { label: 'Work Process', href: '/about/' },
        ],
      },
      {
        title: 'Support',
        links: [
          { label: 'FAQ (Soon)', href: '/' },
          { label: 'Collaboration', href: '/about/' },
        ],
      },
    ],
  },

  {
    groups: [
      {
        title: 'About',
        links: [
          { label: 'Story', href: '/about/' },
          { label: 'Career Path', href: '/about/' },
        ],
      },
    ],
  },
];
