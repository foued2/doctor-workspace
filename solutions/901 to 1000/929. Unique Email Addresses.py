from typing import List


class Solution:
    @staticmethod
    def numUniqueEmails(emails: List[str]) -> int:
        # Initialize a list to store unique email addresses
        table = []

        # Iterate through each email address
        for email in emails:
            # Split the email address into local name and domain name
            local_name, domain_name = email.split('@')

            # Iterate through each character in the local name
            for char in local_name:
                if char == '+':  # Check if the current character is '+'
                    # Remove everything after '+' in the local name
                    local_name = local_name[:local_name.index(char)]
                    break  # Exit the loop after removing the substring

            # Remove '.' characters from the local name
            local_name = local_name.replace(".", "")

            # Concatenate the modified local name and domain name to form the email address
            email = local_name + '@' + domain_name

            # Check if the email address is already in the table
            if email in table:
                continue  # If it's already in the table, move to the next email
            else:
                table.append(email)  # If it's not in the table, add it to the table

        # Return the number of unique email addresses in the table
        return len(table)


print(Solution.numUniqueEmails(
    emails=["fg.r.u.uzj+o.pw@kziczvh.com", "r.cyo.g+d.h+b.ja@tgsg.z.com", "fg.r.u.uzj+o.f.d@kziczvh.com",
            "r.cyo.g+ng.r.iq@tgsg.z.com", "fg.r.u.uzj+lp.k@kziczvh.com", "r.cyo.g+n.h.e+n.g@tgsg.z.com",
            "fg.r.u.uzj+k+p.j@kziczvh.com", "fg.r.u.uzj+w.y+b@kziczvh.com", "r.cyo.g+x+d.c+f.t@tgsg.z.com",
            "r.cyo.g+x+t.y.l.i@tgsg.z.com", "r.cyo.g+brxxi@tgsg.z.com", "r.cyo.g+z+dr.k.u@tgsg.z.com",
            "r.cyo.g+d+l.c.n+g@tgsg.z.com", "fg.r.u.uzj+vq.o@kziczvh.com", "fg.r.u.uzj+uzq@kziczvh.com",
            "fg.r.u.uzj+mvz@kziczvh.com", "fg.r.u.uzj+taj@kziczvh.com", "fg.r.u.uzj+fek@kziczvh.com"]))


class Solution:
    @staticmethod
    def numUniqueEmails(emails: List[str]) -> int:
        """
        Hash table using set()
        """
        # Initialize a set to store unique email addresses
        unique_emails = set()

        # Iterate through each email address
        for email in emails:
            # Split the email address into local name and domain
            local_name, domain = email.split('@')

            # Remove everything after '+' in the local name and remove '.' characters
            local_name = local_name.split('+')[0].replace('.', '')

            # Add the modified email address to the set
            unique_emails.add(local_name + '@' + domain)

        # Return the number of unique email addresses
        return len(unique_emails)
