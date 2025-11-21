module regfile (
    input             clk,
    input             rst,
    input             we,
    input      [3:0]  rs1,
    input      [3:0]  rs2,
    input      [3:0]  rd,
    input      [31:0] wd,
    output     [31:0] rd1,
    output     [31:0] rd2,
    output            parity_error
);
    reg [31:0] regs [0:15];
    reg        parity_bits [0:15];

    integer i;
    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 16; i = i + 1) begin
                regs[i] <= 32'h0;
                parity_bits[i] <= 1'b0;
            end
        end else if (we) begin
            regs[rd] <= wd;
            parity_bits[rd] <= ^wd; // parity is XOR of all bits
        end
    end

    assign rd1 = regs[rs1];
    assign rd2 = regs[rs2];

    wire rs1_parity_mismatch = parity_bits[rs1] ^ (^rd1);
    wire rs2_parity_mismatch = parity_bits[rs2] ^ (^rd2);

    assign parity_error = rs1_parity_mismatch | rs2_parity_mismatch;
endmodule
