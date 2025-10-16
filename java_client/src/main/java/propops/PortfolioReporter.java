package propops;

import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Minimal Java console client for PropOps AI.
 *
 * The tool expects a SQLite JDBC driver on the classpath. It prints
 * total paid revenue and outstanding balances per property to illustrate how a
 * Java-based analytics or BI team could plug into the same data captured by the
 * Python service.
 */
public final class PortfolioReporter {
    private static final String SUMMARY_SQL = """
        SELECT p.name, p.location, p.category,
               IFNULL(SUM(CASE WHEN r.status = 'paid' THEN r.amount END), 0) AS paid,
               IFNULL(SUM(CASE WHEN r.status != 'paid' THEN r.amount END), 0) AS outstanding
        FROM properties p
        LEFT JOIN tenants t ON t.property_id = p.id
        LEFT JOIN rent_invoices r ON r.tenant_id = t.id
        GROUP BY p.id
        ORDER BY p.name
        """;

    private PortfolioReporter() {}

    public static void main(String[] args) throws SQLException {
        if (args.length == 0) {
            System.err.println("Usage: PortfolioReporter <path-to-sqlite-db>");
            System.exit(1);
        }
        Path database = Path.of(args[0]);
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + database.toString())) {
            printSummary(conn);
        }
    }

    private static void printSummary(Connection conn) throws SQLException {
        try (PreparedStatement stmt = conn.prepareStatement(SUMMARY_SQL);
             ResultSet rs = stmt.executeQuery()) {
            System.out.printf("%-25s %-15s %-12s %12s %12s%n", "Property", "Location", "Category", "Paid", "Outstanding");
            System.out.println("-".repeat(80));
            while (rs.next()) {
                System.out.printf(
                    "%-25s %-15s %-12s %12.2f %12.2f%n",
                    rs.getString("name"),
                    rs.getString("location"),
                    rs.getString("category"),
                    rs.getDouble("paid"),
                    rs.getDouble("outstanding")
                );
            }
        }
    }
}
