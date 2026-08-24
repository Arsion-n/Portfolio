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
        title: 'Explore',
        links: [
          { label: 'Projects', href: '/projects/' },
          { label: 'Featured Work', href: '/projects/' },
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
        title: 'Business',
        links: [
          { label: 'Commercial Projects', href: '/projects/' },
          { label: 'Partnerships', href: '/about/' },
        ],
      },
      {
        title: 'Education',
        links: [
          { label: 'Academic Works', href: '/projects/' },
          { label: 'Learning Journey', href: '/about/' },
        ],
      },
      {
        title: 'Public Sector',
        links: [
          { label: 'Urban Concepts', href: '/projects/' },
          { label: 'Community Design', href: '/projects/' },
        ],
      },
    ],
  },
  {
    groups: [
      {
        title: 'Values',
        links: [
          { label: 'Design Principles', href: '/about/' },
          { label: 'Sustainability', href: '/about/' },
        ],
      },
      {
        title: 'About Arison',
        links: [
          { label: 'Story', href: '/about/' },
          { label: 'Career Path', href: '/about/' },
        ],
      },
    ],
  },
];
